from typing import NamedTuple

from reactivated import template


@template
class Index(NamedTuple):
    title: str


@template
class Admin(NamedTuple):
    title: str


@template
class AddClasses(NamedTuple):
    title: str
