from typing import Literal, NamedTuple

from reactivated import Pick, template

from class_tracker.models import School
from discord_tracker.models import DiscordUser

_SchoolPick = Pick[School, Literal["id", "name"]]

_DiscordUserProfilePick = Pick[
    DiscordUser,
    Literal[
        "id",
        "discord_id",
        "username",
        "discriminator",
        "global_name",
        "avatar",
        "is_verified",
        "role",
        "first_login",
        "last_login",
        "login_count",
        "display_name",
        "avatar_url",
    ],
]


@template
class DiscordTrackerIndex(NamedTuple):
    pass


@template
class DiscordTrackerLogin(NamedTuple):
    title: str
    redirect_url: str


@template
class DiscordTrackerProfile(NamedTuple):
    discord_user: _DiscordUserProfilePick
    school: _SchoolPick | None
