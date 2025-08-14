from typing import List, Literal, NamedTuple

from reactivated import Pick, template

from .. import models

_TermPick = Pick[models.Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
_SchoolPick = Pick[models.School, Literal["id", "name", "globalsearch_key"]]
_RecipientPick = Pick[
    models.Recipient,
    Literal[
        "id",
        "name",
        "phone_numbers.id",
        "phone_numbers.number",
        "watched_sections.id",
        "watched_sections.number",
        "watched_sections.topic",
        "watched_sections.course.id",
        "watched_sections.course.code",
        "watched_sections.course.level",
        "watched_sections.instruction_entries.instructor.id",
        "watched_sections.instruction_entries.instructor.name",
    ],
]


@template
class TrackerLogin(NamedTuple):
    is_invalid_credentials: bool = False


@template
class TrackerIndex(NamedTuple):
    title: str


@template
class TrackerAdmin(NamedTuple):
    schools: List[_SchoolPick]
    terms_available: List[_TermPick]


@template
class TrackerAddClasses(NamedTuple):
    terms_available: List[_TermPick]
    recipients: List[_RecipientPick]
