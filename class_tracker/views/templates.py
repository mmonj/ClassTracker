from typing import List, Literal, NamedTuple

from reactivated import Pick, template

from ..models import School, Term

TermPick = Pick[Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
SchoolPick = Pick[School, Literal["id", "name", "globalsearch_key"]]


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
    title: str
    terms_available: List[TermPick]
