import logging
from typing import Any

from allauth.socialaccount.adapter import (  # type: ignore[import-untyped]
    DefaultSocialAccountAdapter,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest

from discord_tracker.models import DiscordUser

logger = logging.getLogger("main")


class DiscordUserConflictError(Exception):
    """raised when a discord account is already linked to another user"""


class DiscordSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    """adapter for Discord social account handling"""

    def populate_user(self, request: HttpRequest, sociallogin: Any, data: dict[str, Any]) -> User:
        """
        Populate base User fields from discord data
        """
        user: User = super().populate_user(request, sociallogin, data)

        logger.info(data)

        # use global_name if available, otherwise username
        display_name = data.get("global_name") or data.get("username", "")
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
            sociallogin.user = existing_discord_user.user
            return

        # fallthrough case: we get here, it's a new discord login with no existing user
        # allauth will handle creating a new user account

    def save_user(self, request: HttpRequest, sociallogin: Any, form: Any = None) -> User:
        """
        Save the user and create associated DiscordUser.
        """
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
            discord_user.verified = discord_data.get("verified", discord_user.verified)
            discord_user.login_count += 1
            discord_user.save()

        return user

    def _get_avatar_url(self, discord_data: dict[str, Any]) -> str:
        """Generate full Discord avatar URL from avatar hash."""
        avatar_hash = discord_data.get("avatar")
        user_id = discord_data.get("id")

        if not avatar_hash or not user_id:
            return ""

        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
