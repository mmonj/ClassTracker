from typing import Literal, TypedDict

from django.http import HttpRequest
from reactivated import Pick

from discord_tracker.models import DiscordUser

_TDiscordUserPick = Pick[
    DiscordUser,
    Literal[
        "id",
        "discord_id",
        "username",
        "discriminator",
        "global_name",
        "avatar",
        "verified",
        # Additional tracking fields
        "first_login",
        "last_login",
        "login_count",
        "display_name",
        "avatar_url",
        # OAuth token info (excluding sensitive tokens)
        "token_expires_at",
        "is_token_expired",
        "can_refresh_token",
    ],
]


class UserInfo(TypedDict):
    name: str
    is_superuser: bool
    is_authenticated: bool
    discord_user: _TDiscordUserPick | None


class User(TypedDict):
    user: UserInfo


def user(request: HttpRequest) -> User:
    discord_user: DiscordUser | None = None
    if request.user.is_authenticated:
        discord_user = DiscordUser.objects.filter(user=request.user).first()

    return {
        "user": {
            "name": request.user.get_username(),
            "is_superuser": request.user.is_superuser,
            "is_authenticated": request.user.is_authenticated,
            "discord_user": discord_user,
        }
    }
