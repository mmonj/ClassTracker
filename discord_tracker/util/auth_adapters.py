import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from allauth.core.exceptions import ImmediateHttpResponse  # type: ignore [import-untyped]
from allauth.socialaccount.adapter import (  # type: ignore [import-untyped]
    DefaultSocialAccountAdapter,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify

from discord_tracker.models import DiscordUser, UserReferral
from server.util.typedefs import Failure, Success, TResult

from .discord_api import check_user_in_trusted_servers

logger = logging.getLogger("main")

TSignupMethod = Literal["trusted_server", "referral"]

# django's base user `username` field has a max length of 150 chars
MAX_USERNAME_LENGTH = 150


class DiscordSocialAccountAdapter(DefaultSocialAccountAdapter):  # type: ignore[misc]
    def populate_user(self, request: HttpRequest, sociallogin: Any, data: dict[str, Any]) -> User:
        """
        Populate base User fields from discord data.
        https://django-allauth.readthedocs.io/en/latest/socialaccount/adapter.html#allauth.socialaccount.adapter.DefaultSocialAccountAdapter.populate_user
        """
        user: User = super().populate_user(request, sociallogin, data)

        discord_data = sociallogin.account.extra_data
        discord_id = discord_data.get("id")

        if discord_id is None:
            logger.error("Discord ID missing from extra_data: %s", discord_data)
            raise ValueError("Discord ID is required but not provided in social login data")

        display_name = discord_data.get("global_name") or discord_data.get("username", "")

        sanitized_name = slugify(display_name) or "user"
        username = f"{sanitized_name}@{discord_id}"

        # Ensure username doesn't exceed Django's max length
        if len(username) > MAX_USERNAME_LENGTH:
            # truncate the the name part, keeping room for the unique `@{discord_id}` part
            max_name_length = MAX_USERNAME_LENGTH - len(f"@{discord_id}")
            sanitized_name = sanitized_name[:max_name_length]
            username = f"{sanitized_name}@{discord_id}"

        user.username = username

        # make sure the base user cannot log in with a password
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
        Invoked just after a user successfully authenticates via a social provider, but before the login is actually processed.
        https://django-allauth.readthedocs.io/en/latest/socialaccount/adapter.html#allauth.socialaccount.adapter.DefaultSocialAccountAdapter.pre_social_login
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
                messages.error(
                    request,
                    "This Discord account is already linked to another user.",
                )
                raise ImmediateHttpResponse(redirect("discord_tracker:login"))
            # else:
            sociallogin.user = request.user
            return

        referral_code = request.session.get("referral_code")
        if "referral_code" in request.session:
            del request.session["referral_code"]

        # if the DiscordUser already exists, update fields
        if existing_discord_user is not None:
            existing_discord_user.login_count += 1
            self._update_tokens(existing_discord_user, sociallogin)
            sociallogin.user = existing_discord_user.user

            existing_discord_user.username = discord_data.get(
                "username", existing_discord_user.username
            )
            existing_discord_user.discriminator = discord_data.get(
                "discriminator", existing_discord_user.discriminator
            )
            existing_discord_user.global_name = discord_data.get(
                "global_name", existing_discord_user.global_name
            )
            existing_discord_user.avatar = self._get_avatar_url(discord_data)
            existing_discord_user.is_verified = discord_data.get(
                "verified", existing_discord_user.is_verified
            )
            existing_discord_user.save()

            return

        # try two methods for signup validation:
        # 1. check if user has a valid referral code
        # 2. check if user is a member of any trusted discord severs

        signup_allowed = False
        referral_to_redeem: UserReferral | None = None
        signup_method: TSignupMethod | None = None

        # 1. validate referral
        referral_result = self._validate_referral(referral_code)
        if referral_result.ok:
            signup_allowed = True
            referral_to_redeem = referral_result.val
            signup_method = "referral"

        # 2. validate trusted server membership
        if not referral_result.ok:
            trusted_membership_result = self._validate_trusted_server_membership(
                sociallogin, discord_data
            )
            if trusted_membership_result.ok:
                signup_allowed = True
                signup_method = "trusted_server"

        if not signup_allowed:
            error_message = (
                "Account creation requires either a valid referral code or membership "
                "in one the special discord servers"
            )
            if not referral_result.ok:
                error_message = f"{referral_result.err}. {error_message}"

            messages.error(request, error_message)
            raise ImmediateHttpResponse(redirect("discord_tracker:login"))

        # stash this sucker for later use
        sociallogin.referral_to_redeem = referral_to_redeem
        sociallogin.signup_method = signup_method

        # allauth looks up its own sociallogin records to see if it should call save_user after this function ends
        # if no sociallogin record exists, then it calls save_user

    def save_user(self, request: HttpRequest, sociallogin: Any, form: Any = None) -> User:
        """
        Save the user and create associated DiscordUser. Only called if internal sociallogin record doesnt exist
        https://django-allauth.readthedocs.io/en/latest/socialaccount/adapter.html#allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user
        """
        # signup validation has passed. create user
        referral_to_redeem: UserReferral | None = sociallogin.referral_to_redeem
        signup_method: TSignupMethod | None = sociallogin.signup_method

        user: User = super().save_user(request, sociallogin, form)

        if sociallogin.account.provider != "discord":
            return user

        discord_data = sociallogin.account.extra_data
        discord_id = discord_data.get("id")

        if not discord_id:
            return user

        discord_user = DiscordUser.objects.create(
            discord_id=discord_id,
            user=user,
            username=discord_data.get("username", ""),
            discriminator=discord_data.get("discriminator", ""),
            global_name=discord_data.get("global_name", ""),
            avatar=self._get_avatar_url(discord_data),
            is_verified=discord_data.get("verified", False),
            login_count=1,
            access_token=getattr(sociallogin.token, "token", ""),
            refresh_token=getattr(sociallogin.token, "token_secret", ""),
            token_expires_at=self._get_token_expiry(sociallogin),
        )

        # redeem referral or redeem via trusted server membership
        if referral_to_redeem is not None and signup_method == "referral":
            referral_to_redeem.redeem(discord_user)
            logger.info(
                "User %s signed up via referral code %s",
                discord_user.display_name,
                referral_to_redeem.code,
            )
        elif signup_method == "trusted_server":
            logger.info(
                "User %s signed up via trusted server membership", discord_user.display_name
            )

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
                return datetime.fromtimestamp(float(expires_at), tz=UTC)
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

    def _validate_trusted_server_membership(
        self, sociallogin: Any, discord_data: dict[str, Any]
    ) -> TResult[bool, str]:
        """Return Success(True) if user is in a trusted server, Failure with error message otherwise"""
        access_token = getattr(sociallogin.token, "token", "")
        if not access_token:
            return Failure("No Discord access token available for server membership check")

        trusted_membership_result = check_user_in_trusted_servers(access_token)
        if not trusted_membership_result.ok:
            logger.warning(
                "Failed to check trusted server membership for user %s: %s",
                discord_data.get("username", "unknown"),
                trusted_membership_result.err,
            )
            return Failure(f"Failed to verify server membership: {trusted_membership_result.err}")

        if trusted_membership_result.val:
            logger.info(
                "User %s allowed signup via trusted server membership",
                discord_data.get("username", "unknown"),
            )
            return Success(True)

        return Failure("User is not a member of any trusted Discord servers")

    def _validate_referral(self, referral_code: str | None) -> TResult[UserReferral, str]:
        # check if referral code is correct

        if referral_code is None:
            return Failure("You need a referral code to create a new account on this website")

        referral_to_redeem = UserReferral.objects.filter(code=referral_code).first()

        if referral_to_redeem is None or not referral_to_redeem.is_valid():
            return Failure("Your referral code is invalid or has expired")

        return Success(referral_to_redeem)
