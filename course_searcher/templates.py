from typing import NamedTuple

from reactivated import template


@template
class AddClasses(NamedTuple):
    title: str
