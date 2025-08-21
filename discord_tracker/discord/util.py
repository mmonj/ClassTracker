import re
from urllib.parse import urlparse

import cattrs
import requests

from server.util import init_http_retrier

from .typedefs import TChannelData, TDiscordInviteData, TGuildAssetUrls, TGuildData, TInviterData

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


def get_discord_invite_info(invite_code: str, timeout: int = 15) -> TDiscordInviteData:
    """Fetch Discord invite information using the invite code."""
    invite_info_url = DISCORD_INVITE_TEMPLATE.format(invite_code=invite_code)
    session = init_http_retrier()

    try:
        resp = session.get(invite_info_url, timeout=timeout)
        resp.raise_for_status()
        return cattrs.structure(resp.json(), TDiscordInviteData)
    except requests.HTTPError as e:
        raise DiscordAPIError(f"Failed to fetch invite info: {e}") from e


def get_guild_icon_url(
    guild_id: str, icon_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    """Generate the URL for a Discord guild's icon."""
    if not icon_hash:
        return None

    return GUILD_ICON_URL_TEMPLATE.format(
        guild_id=guild_id, icon_hash=icon_hash, file_extension=file_extension
    )


def get_guild_banner_url(
    guild_id: str, banner_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    """Generate the URL for a Discord guild's banner."""
    if not banner_hash:
        return None

    return GUILD_BANNER_URL_TEMPLATE.format(
        guild_id=guild_id, banner_hash=banner_hash, file_extension=file_extension
    )


def get_guild_splash_url(
    guild_id: str, splash_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    """Generate the URL for a Discord guild's splash image."""
    if not splash_hash:
        return None

    return GUILD_SPLASH_URL_TEMPLATE.format(
        guild_id=guild_id, splash_hash=splash_hash, file_extension=file_extension
    )


def get_user_avatar_url(
    user_id: str, avatar_hash: str | None, file_extension: str = "jpg"
) -> str | None:
    """Generate the URL for a Discord user's avatar."""
    if not avatar_hash:
        return None

    return USER_AVATAR_URL_TEMPLATE.format(
        user_id=user_id, avatar_hash=avatar_hash, file_extension=file_extension
    )


def get_guild_info_from_invite(invite_code: str) -> TGuildData:
    invite_info = get_discord_invite_info(invite_code)
    return invite_info["guild"]


def get_inviter_info_from_invite(invite_code: str) -> TInviterData:
    invite_info = get_discord_invite_info(invite_code)
    return invite_info["inviter"]


def get_channel_info_from_invite(invite_code: str) -> TChannelData:
    invite_info = get_discord_invite_info(invite_code)
    return invite_info["channel"]


def format_guild_info(guild: TGuildData) -> str:
    """Format guild information into a readable string."""
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


def format_inviter_info(inviter: TInviterData) -> str:
    """Format inviter information into a readable string."""
    display_name = inviter["global_name"] or inviter["username"]

    return f"""Inviter Information:
- Display Name: {display_name}
- Username: {inviter["username"]}
- ID: {inviter["id"]}
- Discriminator: {inviter["discriminator"]}
- Public Flags: {inviter["public_flags"]}
- Flags: {inviter["flags"]}"""


def is_guild_partnered(guild: TGuildData) -> bool:
    """Check if a guild is Discord partnered."""
    return "PARTNERED" in guild["features"]


def is_guild_verified(guild: TGuildData) -> bool:
    """Check if a guild is Discord verified."""
    return "VERIFIED" in guild["features"]


def has_guild_vanity_url(guild: TGuildData) -> bool:
    """Check if a guild has a vanity URL."""
    return "VANITY_URL" in guild["features"]


def get_all_guild_asset_urls(guild: TGuildData, file_extension: str = "jpg") -> TGuildAssetUrls:
    """Get all available asset URLs for a guild."""
    guild_id = guild["id"]

    return {
        "icon": get_guild_icon_url(guild_id, guild["icon"], file_extension),
        "banner": get_guild_banner_url(guild_id, guild["banner"], file_extension),
        "splash": get_guild_splash_url(guild_id, guild["splash"], file_extension),
    }


def extract_invite_code_from_url(invite_url: str) -> str | None:
    """Assumes invite_url is a valid url"""
    invite_url = re.sub(r"^https?://", "https://", invite_url, flags=re.IGNORECASE)
    if not invite_url.startswith(DISCORD_INVITE_URL_PREFIXES):
        return None

    invite_url = invite_url.strip(" /")
    parsed_url = urlparse(invite_url)

    if parsed_url.path == "":
        return None
    return parsed_url.path.split("/")[-1]


def is_valid_invite_code(code: str) -> bool:
    if code.strip() == "":
        return False
    return bool(re.match(r"^[a-zA-Z0-9-]{6,25}$", code))
