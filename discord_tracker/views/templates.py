from typing import Literal, NamedTuple

from reactivated import Pick, template

from class_tracker.models import School
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser
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
        "subjects.id",
        "subjects.name",
        "courses.id",
        "courses.code",
        "courses.level",
        "courses.title",
        "instructors.id",
        "instructors.name",
    ],
]

_DiscordInvitePick = Pick[
    DiscordInvite,
    Literal[
        "id",
        "invite_url",
        "notes_md",
        "is_valid",
        "expires_at",
        "datetime_created",
        "submitter.display_name",
        "submitter.role_info",
        "discord_server.display_name",
        "discord_server.icon_url",
        "discord_server.privacy_level",
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
class DiscordTrackerServerListings(NamedTuple):
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


@template
class DiscordTrackerUnapprovedInvites(NamedTuple):
    unapproved_invites: list[_DiscordInvitePick]
