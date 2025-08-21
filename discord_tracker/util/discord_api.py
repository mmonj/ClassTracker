import logging
from datetime import timedelta
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

from discord_tracker.models import DiscordUser
from server.util import init_http_retrier

logger = logging.getLogger("main")


class DiscordAPIError(Exception):
    """raised when discord API calls fail."""


def refresh_discord_token(discord_user: DiscordUser) -> bool:
    """
    Refresh the discord OAuth token for a user.
    Returns True if successful, False otherwise.
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
    """
    Fetch user's current profile
    """
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
    Sync the user's Discord profile data with local db.
    Returns True if successful, False otherwise.
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
