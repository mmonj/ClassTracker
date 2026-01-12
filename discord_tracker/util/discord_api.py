import datetime
import logging
import re
from datetime import timedelta
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import cattrs
import requests
from django.conf import settings
from django.utils import timezone

from discord_tracker.models import DiscordUser
from discord_tracker.typedefs.discord_api import TDiscordInviteData, TGuildData
from discord_tracker.typedefs.discord_partials import (
    TBaseGuildData,
    TBaseUserData,
    TChannelData,
    TGuildAssetUrls,
)
from server.util import init_http_retrier
from server.util.typedefs import Failure, Success, TResult

logger = logging.getLogger("main")

# jan 1, 2015 00:00:00 UTC, in ms
DISCORD_EPOCH = 1420070400000

DISCORD_INVITE_URL_PREFIXES = (
    "https://discord.gg/",
    "https://discord.com/invite/",
    "https://discordapp.com/invite/",
)

DISCORD_INVITE_TEMPLATE = "https://discord.com/api/v10/invites/{invite_code}"
GUILD_ICON_URL_TEMPLATE = "https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.{file_extension}"
GUILD_BANNER_URL_TEMPLATE = (
    "https://cdn.discordapp.com/banners/{guild_id}/{banner_hash}.{file_extension}"
)
GUILD_SPLASH_URL_TEMPLATE = (
    "https://cdn.discordapp.com/splashes/{guild_id}/{splash_hash}.{file_extension}"
)
USER_AVATAR_URL_TEMPLATE = (
    "https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{file_extension}"
)


class DiscordAPIError(Exception):
    pass


def refresh_discord_token(discord_user: DiscordUser) -> bool:
    """
    Refresh the discord OAuth token for a user. Returns true if success
    """
    if not discord_user.refresh_token:
        logger.warning("No refresh token available for user %s", discord_user.user.username)
        return False

    # discord token refresh endpoint
    url = "https://discord.com/api/oauth2/token"

    # get discord client credentials from settings
    discord_config = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get("discord", {})
    app_config = discord_config.get("APP", {})

    data = {
        "client_id": app_config.get("client_id"),
        "client_secret": app_config.get("secret"),
        "grant_type": "refresh_token",
        "refresh_token": discord_user.refresh_token,
    }

    try:
        session = init_http_retrier()
        response = session.post(url, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()

        # update the stored tokens
        discord_user.access_token = token_data.get("access_token", "")
        discord_user.refresh_token = token_data.get("refresh_token", discord_user.refresh_token)

        # calculate expiry time
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        discord_user.token_expires_at = timezone.now() + timedelta(seconds=expires_in)

        discord_user.save(update_fields=["access_token", "refresh_token", "token_expires_at"])
        logger.info("Successfully refreshed token for user %s", discord_user.user.username)
        return True

    except requests.RequestException:
        logger.exception("Failed to refresh token for user %s", discord_user.user.username)
        return False


def fetch_discord_user_profile(discord_user: DiscordUser) -> dict[str, Any] | None:
    if not discord_user.access_token:
        logger.warning("No access token available for user %s", discord_user.user.username)
        return None

    # Check if token is expired and try to refresh
    if discord_user.token_expires_at and discord_user.token_expires_at <= timezone.now():
        logger.info("Token expired for user %s, attempting refresh", discord_user.user.username)
        if not refresh_discord_token(discord_user):
            return None

    url = "https://discord.com/api/users/@me"
    headers = {
        "Authorization": f"Bearer {discord_user.access_token}",
        "Content-Type": "application/json",
    }

    try:
        session = init_http_retrier()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        profile_data: dict[str, Any] = response.json()
        return profile_data

    except requests.RequestException:
        logger.exception("Failed to fetch profile for user %s", discord_user.user.username)
        return None


def sync_discord_profile(discord_user: DiscordUser) -> bool:
    """
    Sync the user's Discord profile data with local db. Returns true if successful
    """
    profile_data = fetch_discord_user_profile(discord_user)

    if not profile_data:
        return False

    # update user profile fields
    discord_user.username = profile_data.get("username", discord_user.username)
    discord_user.discriminator = profile_data.get("discriminator", discord_user.discriminator)
    discord_user.global_name = profile_data.get("global_name", discord_user.global_name)
    discord_user.is_verified = profile_data.get("verified", discord_user.is_verified)

    # update avatar
    avatar_hash = profile_data.get("avatar")
    if avatar_hash:
        discord_user.avatar = (
            f"https://cdn.discordapp.com/avatars/{discord_user.discord_id}/{avatar_hash}.png"
        )

    discord_user.save(
        update_fields=["username", "discriminator", "global_name", "verified", "avatar"]
    )

    logger.info("Successfully synced profile for user %s", discord_user.user.username)
    return True


def get_discord_invite_info(
    invite_code: str, timeout: int = 15
) -> TResult[TDiscordInviteData, DiscordAPIError]:
    invite_info_url = DISCORD_INVITE_TEMPLATE.format(invite_code=invite_code)
    session = init_http_retrier()

    try:
        resp = session.get(invite_info_url, timeout=timeout)
        resp.raise_for_status()
        return Success(cattrs.structure(resp.json(), TDiscordInviteData))
    except requests.HTTPError as e:
        return Failure(DiscordAPIError(f"Failed to fetch invite info: {e}"))


def get_guild_icon_url(guild_id: str, icon_hash: str | None, file_extension: str = "jpg") -> str:
    if not icon_hash:
        return ""

    base_url = GUILD_ICON_URL_TEMPLATE.format(
        guild_id=guild_id, icon_hash=icon_hash, file_extension=file_extension
    )

    parsed_url = urlparse(base_url)
    query = parse_qs(parsed_url.query)
    query["size"] = ["256"]  # icon size
    new_query = urlencode(query, doseq=True)

    return urlunparse(parsed_url._replace(query=new_query))


def get_guild_banner_url(
    guild_id: str, banner_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    if not banner_hash:
        return None

    return GUILD_BANNER_URL_TEMPLATE.format(
        guild_id=guild_id, banner_hash=banner_hash, file_extension=file_extension
    )


def get_guild_splash_url(
    guild_id: str, splash_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    if not splash_hash:
        return None

    return GUILD_SPLASH_URL_TEMPLATE.format(
        guild_id=guild_id, splash_hash=splash_hash, file_extension=file_extension
    )


def get_user_avatar_url(
    user_id: str, avatar_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    if not avatar_hash:
        return None

    return USER_AVATAR_URL_TEMPLATE.format(
        user_id=user_id, avatar_hash=avatar_hash, file_extension=file_extension
    )


def get_guild_info_from_invite(invite_code: str) -> TResult[TGuildData, DiscordAPIError]:
    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return Failure(invite_result.err)
    return Success(invite_result.val["guild"])


def get_inviter_info_from_invite(invite_code: str) -> TResult[TBaseUserData, DiscordAPIError]:
    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return Failure(invite_result.err)
    return Success(invite_result.val["inviter"])


def get_channel_info_from_invite(invite_code: str) -> TResult[TChannelData, DiscordAPIError]:
    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return Failure(invite_result.err)
    return Success(invite_result.val["channel"])


def format_guild_info(guild: TGuildData) -> str:
    """Format guild information into a nicely formatted string"""
    features = ", ".join(guild["features"]) if guild["features"] else "None"
    nsfw_status = "Yes" if guild["nsfw"] else "No"

    return f"""Guild Information:
- Name: {guild["name"]}
- ID: {guild["id"]}
- Description: {guild["description"] or "None"}
- Verification Level: {guild["verification_level"]}
- NSFW: {nsfw_status}
- Premium Subscriptions: {guild["premium_subscription_count"]}
- Features: {features}"""


def format_inviter_info(inviter: TBaseUserData) -> str:
    """Format inviter information into a nicely formatted string"""
    display_name = inviter["global_name"] or inviter["username"]

    return f"""Inviter Information:
- Display Name: {display_name}
- Username: {inviter["username"]}
- ID: {inviter["id"]}
- Discriminator: {inviter["discriminator"]}
- Public Flags: {inviter["public_flags"]}
- Flags: {inviter["flags"]}"""


def is_guild_partnered(guild: TGuildData) -> bool:
    return "PARTNERED" in guild["features"]


def is_guild_verified(guild: TGuildData) -> bool:
    return "VERIFIED" in guild["features"]


def has_guild_vanity_url(guild: TGuildData) -> bool:
    return "VANITY_URL" in guild["features"]


def get_all_guild_asset_urls(guild: TGuildData, file_extension: str = "jpg") -> TGuildAssetUrls:
    guild_id = guild["id"]

    return TGuildAssetUrls(
        icon=get_guild_icon_url(guild_id, guild["icon"], file_extension),
        banner=get_guild_banner_url(guild_id, guild["banner"], file_extension),
        splash=get_guild_splash_url(guild_id, guild["splash"], file_extension),
    )


def extract_invite_code_from_url(invite_url: str) -> str | None:
    """Assumes invite_url is a valid url"""
    invite_url = re.sub(r"^https?://", "https://", invite_url, flags=re.IGNORECASE)
    if not invite_url.startswith(DISCORD_INVITE_URL_PREFIXES):
        return None

    invite_url = invite_url.strip(" /")
    parsed_url = urlparse(invite_url)

    if parsed_url.path == "":
        return None

    code = parsed_url.path.split("/")[-1]
    return code if _is_valid_invite_code(code) else None


def _is_valid_invite_code(code: str) -> bool:
    code = code.strip()
    if code == "":
        return False

    match = re.match(r"^[a-zA-Z0-9-]{6,25}$", code)
    if match is None:
        logger.error("Invalid invite code format: %s", code)

    return bool(match)


def fetch_user_guilds(access_token: str) -> TResult[list[TBaseGuildData], str]:
    """
    Fetch the user's Discord guilds using their access token.
    Returns a list of guild objects or an error message.
    """
    url = "https://discord.com/api/users/@me/guilds"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        session = init_http_retrier()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        guilds = response.json()

        return Success(cattrs.structure(guilds, list[TBaseGuildData]))

    except requests.RequestException:
        logger.exception("Failed to fetch user guilds")
        return Failure("Failed to fetch Discord guilds")


def get_guild_creation_date(guild_id: str) -> datetime.datetime:
    timestamp_ms = (int(guild_id) >> 22) + DISCORD_EPOCH

    return datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.UTC)
