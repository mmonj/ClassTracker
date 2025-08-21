import logging
from datetime import datetime, timedelta
from os import getuid
from typing import Any

from allauth.socialaccount.adapter import (  # type: ignore[import-untyped]
    DefaultSocialAccountAdapter,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone

from discord_tracker.models import DiscordUser

logger = logging.getLogger("main")


class DiscordUserConflictError(Exception):
    """raised when a discord account is already linked to another user"""


class DiscordSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    """adapter for Discord social account handling"""

    def populate_user(self, request: HttpRequest, sociallogin: Any, data: dict[str, Any]) -> User:
        """Populate base User fields from discord data"""
        user: User = super().populate_user(request, sociallogin, data)

        discord_id = data.get("id", getuid())
        display_name = data.get("global_name") or data.get("username", "")
        user.username = f"{display_name}@{discord_id}"

        # ensure the user cannot log in with a password
        user.set_unusable_password()

        if display_name:
            # set first_name and last_name based on display name
            name_parts = display_name.split(" ", 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]

        return user

    def pre_social_login(self, request: HttpRequest, sociallogin: Any) -> None:
        """
        Handle pre-login logic for discord accounts
        This is called before the user is logged in.
        """
        super().pre_social_login(request, sociallogin)

        if sociallogin.account.provider != "discord":
            return

        discord_data = sociallogin.account.extra_data
        discord_id = discord_data.get("id")

        if not discord_id:
            return

        existing_discord_user = (
            DiscordUser.objects.filter(discord_id=discord_id).select_related("user").first()
        )

        if request.user.is_authenticated:
            # make sure this discord account isn't already linked to someone else
            if existing_discord_user is not None and existing_discord_user.user != request.user:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "This Discord account is already linked to another user.",
                )
                raise DiscordUserConflictError("Discord account already linked to another user.")
            # else:
            sociallogin.user = request.user
            return

        if existing_discord_user is not None:
            existing_discord_user.login_count += 1
            self._update_tokens(existing_discord_user, sociallogin)
            existing_discord_user.save(
                update_fields=["login_count", "access_token", "refresh_token", "token_expires_at"]
            )
            sociallogin.user = existing_discord_user.user
            return

        # fallthrough case: we get here, it's a new discord login with no existing user
        # allauth will handle creating a new user account

    def save_user(self, request: HttpRequest, sociallogin: Any, form: Any = None) -> User:
        """Save the user and create associated DiscordUser."""
        user: User = super().save_user(request, sociallogin, form)

        if sociallogin.account.provider != "discord":
            return user

        discord_data = sociallogin.account.extra_data
        discord_id = discord_data.get("id")

        if not discord_id:
            return user

        # Create or update DiscordUser
        discord_user, created = DiscordUser.objects.get_or_create(
            discord_id=discord_id,
            defaults={
                "user": user,
                "username": discord_data.get("username", ""),
                "discriminator": discord_data.get("discriminator", ""),
                "global_name": discord_data.get("global_name", ""),
                "avatar": self._get_avatar_url(discord_data),
                "verified": discord_data.get("verified", False),
                "login_count": 1,
                "access_token": getattr(sociallogin.token, "token", ""),
                "refresh_token": getattr(sociallogin.token, "token_secret", ""),
                "token_expires_at": self._get_token_expiry(sociallogin),
            },
        )

        # if the DiscordUser already exists, update fields
        if not created:
            discord_user.username = discord_data.get("username", discord_user.username)
            discord_user.discriminator = discord_data.get(
                "discriminator", discord_user.discriminator
            )
            discord_user.global_name = discord_data.get("global_name", discord_user.global_name)
            discord_user.avatar = self._get_avatar_url(discord_data)
            discord_user.is_verified = discord_data.get("verified", discord_user.is_verified)
            discord_user.login_count += 1
            self._update_tokens(discord_user, sociallogin)
            discord_user.save()

        return user

    def _update_tokens(self, discord_user: DiscordUser, sociallogin: Any) -> None:
        """Update OAuth tokens for a DiscordUser instance."""
        discord_user.access_token = getattr(sociallogin.token, "token", "")
        discord_user.refresh_token = getattr(sociallogin.token, "token_secret", "")
        discord_user.token_expires_at = self._get_token_expiry(sociallogin)

    def _get_token_expiry(self, sociallogin: Any) -> datetime | None:
        """Calculate token expiry time from sociallogin token."""
        if hasattr(sociallogin.token, "expires_at") and sociallogin.token.expires_at:
            # if not already datetime, convert it
            expires_at = sociallogin.token.expires_at
            if isinstance(expires_at, datetime):
                return expires_at
            # convert if it is timestamp
            try:
                return datetime.fromtimestamp(float(expires_at), tz=timezone.get_current_timezone())
            except (ValueError, TypeError):
                pass

        # https://github.com/reddit-archive/reddit/wiki/OAuth2#refreshing-the-token
        # discord access tokens will normally expire in 1 hour
        # if we don't have explicit expiry info, calculate it
        return timezone.now() + timedelta(hours=1)

    def _get_avatar_url(self, discord_data: dict[str, Any]) -> str:
        """Generate full Discord avatar URL from avatar hash."""
        avatar_hash = discord_data.get("avatar")
        user_id = discord_data.get("id")

        if not avatar_hash or not user_id:
            return ""

        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
