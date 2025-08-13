from typing import List, Literal, NamedTuple

from reactivated import Pick, interface

from ..models import ContactInfo, Course, CourseSection, Recipient, School, Subject, Term
from .forms import ContactInfoForm, RecipientForm

_TermPick = Pick[Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
_SchoolPick = Pick[School, Literal["id", "name", "globalsearch_key"]]
_SubjectPick = Pick[Subject, Literal["id", "name"]]
_SectionPick = Pick[
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

_RecipientPick = Pick[
    Recipient,
    Literal[
        "id",
        "name",
        "phone_numbers.id",
        "phone_numbers.number",
    ],
]

ContactPick = Pick[ContactInfo, Literal["id", "number", "is_enabled"]]


@interface
class BasicResponse(NamedTuple):
    is_success: bool = True
    message: str = ""


@interface
class RespSchoolsTermsUpdate(NamedTuple):
    available_schools: List[_SchoolPick]
    available_terms: List[_TermPick]
    new_terms_count: int


@interface
class RespSubjectsUpdate(NamedTuple):
    available_subjects: List[_SubjectPick]


@interface
class RespGetSubjects(NamedTuple):
    subjects: List[_SubjectPick]


@interface
class RespRefreshCourseSections(NamedTuple):
    courses: List[Pick[Course, Literal["id", "code", "level", "sections.number"]]]


@interface
class RespGetRecipientForm(NamedTuple):
    recipient_form: RecipientForm
    contact_info_forms: list[ContactInfoForm]
    new_contact_info_form: ContactInfoForm


@interface
class RespEditRecipient(NamedTuple):
    recipient: _RecipientPick | None
    recipient_form: RecipientForm | None
    contact_info_forms: list[ContactInfoForm] | None
    new_contact_info_form: ContactInfoForm | None


@interface
class RespAddWatchedSection(NamedTuple):
    added_section: _SectionPick
