from typing import Literal, NamedTuple, TypedDict

from reactivated import Pick, interface

from class_tracker.models import Course, Instructor, School, Subject
from discord_tracker.models import DiscordInvite, DiscordServer

_DiscordInvitePick = Pick[
    DiscordInvite,
    Literal[
        "id",
        "invite_url",
        "notes_md",
        "expires_at",
        "max_uses",
        "uses_count",
        "is_valid",
    ],
]

_DiscordServerPick = Pick[
    DiscordServer,
    Literal[
        "id",
        "server_id",
        "name",
        "display_name",
        "description",
        "icon_url",
        "privacy_level",
        "is_active",
        ##
        "schools.id",
        "schools.name",
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

_SchoolPick = Pick[School, Literal["id", "name"]]
_SubjectPick = Pick[Subject, Literal["id", "name"]]
_CoursePick = Pick[Course, Literal["id", "code", "level", "title"]]
_InstructorPick = Pick[Instructor, Literal["id", "name"]]


@interface
class SchoolSelectionResponse(NamedTuple):
    success: bool
    message: str


@interface
class GetAvailableSchoolsResponse(NamedTuple):
    success: bool
    available_schools: list[_SchoolPick]
    message: str


@interface
class ValidateInviteResponse(NamedTuple):
    success: bool
    message: str
    guild_name: str
    guild_id: str
    available_schools: list[_SchoolPick]


class TSimpleGuildInfo(TypedDict):
    id: str
    name: str
    icon_url: str


@interface
class ValidateDiscordInviteResponse(NamedTuple):
    guild_info: TSimpleGuildInfo | None
    existing_server_info: _DiscordServerPick | None
    available_schools: list[_SchoolPick]
    is_new_server: bool


@interface
class ServerInvitesResponse(NamedTuple):
    success: bool
    invites: list[_DiscordInvitePick]
    message: str


@interface
class SubmitInviteResponse(NamedTuple):
    discord_server: _DiscordServerPick | None


@interface
class GetSubjectsResponse(NamedTuple):
    subjects: list[_SubjectPick]
    message: str


@interface
class GetCoursesResponse(NamedTuple):
    courses: list[_CoursePick]
    message: str


@interface
class GetInstructorsResponse(NamedTuple):
    instructors: list[_InstructorPick]
    message: str
