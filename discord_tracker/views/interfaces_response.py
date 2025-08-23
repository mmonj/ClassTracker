from typing import NamedTuple

from reactivated import interface


@interface
class SchoolSelectionResponse(NamedTuple):
    success: bool
    message: str
