from typing import List, Literal, NamedTuple

from reactivated import Pick, template

from .. import models

TermPick = Pick[models.Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
SchoolPick = Pick[models.School, Literal["id", "name", "globalsearch_key"]]
RecipientPick = Pick[
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
    schools: List[SchoolPick]
    terms_available: List[TermPick]


@template
class TrackerAddClasses(NamedTuple):
    terms_available: List[TermPick]
    recipients: List[RecipientPick]
