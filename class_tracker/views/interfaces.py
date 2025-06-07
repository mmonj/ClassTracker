from typing import List, Literal, NamedTuple

from reactivated import Pick, interface

from ..models import Course, School, Subject, Term

TermPick = Pick[Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
SchoolPick = Pick[School, Literal["id", "name", "globalsearch_key"]]
SubjectPick = Pick[Subject, Literal["id", "name"]]


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
