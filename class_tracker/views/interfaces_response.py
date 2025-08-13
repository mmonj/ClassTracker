from typing import List, Literal, NamedTuple

from reactivated import Pick, interface

from ..models import ContactInfo, Course, CourseSection, Recipient, School, Subject, Term
from .forms import ContactInfoForm, RecipientForm

TermPick = Pick[Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
SchoolPick = Pick[School, Literal["id", "name", "globalsearch_key"]]
SubjectPick = Pick[Subject, Literal["id", "name"]]
SectionPick = Pick[
    CourseSection,
    Literal[
        "id",
        "number",
        "topic",
        "course.id",
        "course.code",
        "course.level",
    ],
]
ContactPick = Pick[ContactInfo, Literal["id", "number", "is_enabled"]]


@interface
class BasicResponse(NamedTuple):
    is_success: bool = True
    message: str = ""


@interface
class RespSchoolsTermsUpdate(NamedTuple):
    available_schools: List[SchoolPick]
    available_terms: List[TermPick]
    new_terms_count: int


@interface
class RespSubjectsUpdate(NamedTuple):
    available_subjects: List[SubjectPick]


@interface
class RespGetSubjects(NamedTuple):
    subjects: List[SubjectPick]


@interface
class RespRefreshCourseSections(NamedTuple):
    courses: List[Pick[Course, Literal["id", "code", "level", "sections.number"]]]


@interface
class RespGetRecipientForm(NamedTuple):
    recipient_form: RecipientForm
    contact_info_forms: list[ContactInfoForm]


@interface
class RespEditRecipient(NamedTuple):
    recipient: Pick[Recipient, Literal["id", "name", "description"]] | None
    contact_infos: list[ContactPick] | None
    recipient_form: RecipientForm | None
    contact_info_forms: list[ContactInfoForm] | None


@interface
class RespAddWatchedSection(NamedTuple):
    added_section: SectionPick
