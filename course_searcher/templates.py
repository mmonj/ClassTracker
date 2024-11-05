from typing import List, NamedTuple

from reactivated import Pick, template

from .models import Term


@template
class Index(NamedTuple):
    title: str


@template
class Admin(NamedTuple):
    title: str
    terms_available: List[Pick[Term, "id", "name", "year"]]


@template
class AddClasses(NamedTuple):
    title: str
