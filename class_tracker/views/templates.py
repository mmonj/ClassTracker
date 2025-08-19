from typing import List, Literal, NamedTuple

from reactivated import Pick, template

from .. import models
from .typedefs import TPaginationData

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

_ClassAlertPick = Pick[
    models.ClassAlert,
    Literal[
        "id",
        "datetime_created",
        "recipient.id",
        "recipient.name",
        "course_section.id",
        "course_section.number",
        "course_section.topic",
        "course_section.course.id",
        "course_section.course.code",
        "course_section.course.level",
        "course_section.course.subject.name",
        "course_section.term.id",
        "course_section.term.full_term_name",
        "course_section.instruction_entries.id",
        "course_section.instruction_entries.get_days_and_times",
        "course_section.instruction_entries.instructor.id",
        "course_section.instruction_entries.instructor.name",
    ],
]

_RecipientBasicPick = Pick[models.Recipient, Literal["id", "name"]]


@template
class ClassTrackerLogin(NamedTuple):
    is_invalid_credentials: bool = False


@template
class ClassTrackerIndex(NamedTuple):
    title: str


@template
class ClassTrackerManageCourselist(NamedTuple):
    schools: List[_SchoolPick]
    terms_available: List[_TermPick]


@template
class ClassTrackerAddClasses(NamedTuple):
    terms_available: List[_TermPick]
    recipients: List[_RecipientPick]


@template
class ClassTrackerClassAlerts(NamedTuple):
    title: str
    class_alerts: List[_ClassAlertPick]
    recipients: List[_RecipientBasicPick]
    selected_recipient_id: int
    pagination: TPaginationData
