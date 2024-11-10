from typing import List, Literal, NamedTuple

from reactivated import Pick, template

from .models import School, Term

TermPick = Pick[Term, Literal["id", "name", "year", "globalsearch_key", "full_term_name"]]
SchoolPick = Pick[School, Literal["id", "name", "globalsearch_key"]]


@template
class Index(NamedTuple):
    title: str


@template
class Admin(NamedTuple):
    title: str
    schools: List[SchoolPick]
    terms_available: List[TermPick]


@template
class AddClasses(NamedTuple):
    title: str
    terms_available: List[TermPick]
