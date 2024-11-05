from typing import NamedTuple

from reactivated import interface


@interface
class BasicResponse(NamedTuple):
    is_success: bool = True
    message: str = ""
