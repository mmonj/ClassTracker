from typing import Literal, NamedTuple

from reactivated import Pick, template

from class_tracker.models import School
from discord_tracker.models import DiscordServer, DiscordUser
from discord_tracker.views.forms import SchoolSelectionForm

_SchoolPick = Pick[School, Literal["id", "name"]]

_DiscordServerPick = Pick[
    DiscordServer,
    Literal[
        "id",
        "server_id",
        "name",
        "icon_url",
        "privacy_level",
        "custom_title",
        "description",
        "is_active",
        "display_name",
        "is_general_server",
    ],
]

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
        "role_info",
        "first_login",
        "last_login",
        "login_count",
        "display_name",
        "avatar_url",
    ],
]


@template
class DiscordTrackerIndex(NamedTuple):
    public_servers: list[_DiscordServerPick]
    privileged_servers: list[_DiscordServerPick]


@template
class DiscordTrackerLogin(NamedTuple):
    pass


@template
class DiscordTrackerProfile(NamedTuple):
    discord_user: _DiscordUserProfilePick
    school: _SchoolPick | None
    school_form: SchoolSelectionForm
    show_school_modal: bool
