from typing import Literal, NamedTuple

from reactivated import Pick, template

from class_tracker.models import School
from discord_tracker.models import (
    Alert,
    DiscordInvite,
    DiscordServer,
    DiscordUser,
    UserAlert,
    UserReferral,
)
from discord_tracker.views.forms import ReferralCreationForm, SchoolSelectionForm
from server.util.typedefs import TPaginationData

_SchoolPick = Pick[School, Literal["id", "name"]]

_DiscordServerPick = Pick[
    DiscordServer,
    Literal[
        "id",
        "server_id",
        "name",
        "icon_url",
        "member_count",
        "privacy_level_info",
        "custom_title",
        "description",
        "is_active",
        "is_featured",
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
        "datetime_established",
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
        "discord_server.privacy_level_info",
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

_UserReferralPick = Pick[
    UserReferral,
    Literal[
        "id",
        "code",
        "max_uses",
        "num_uses",
        "datetime_created",
        "datetime_expires",
        "expiry_timeframe",
        "is_valid",
        "is_expired",
    ],
]

_AlertPick = Pick[
    Alert,
    Literal[
        "id",
        "title",
        "datetime_created",
    ],
]

_UserAlertPick = Pick[
    UserAlert,
    Literal[
        "id",
        "is_read",
        "alert.title",
        "alert.datetime_created",
    ],
]


@template
class DiscordTrackerWelcome(NamedTuple):
    servers: list[_DiscordServerPick]
    pending_invites_count: int


@template
class DiscordTrackerExploreAll(NamedTuple):
    servers: list[_DiscordServerPick]
    pagination: TPaginationData | None
    subject_id: int | None
    course_id: int | None
    is_search_active: bool
    pending_invites_count: int


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


@template
class DiscordTrackerReferralManagement(NamedTuple):
    referral_form: ReferralCreationForm
    referrals: list[_UserReferralPick]
    pagination: TPaginationData


@template
class DiscordTrackerAlerts(NamedTuple):
    alerts: list[_UserAlertPick]
