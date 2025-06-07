import re
from dataclasses import dataclass
from typing import Generic, Literal, TypeAlias, TypedDict, TypeVar

from django.contrib.auth.models import User
from django.http import HttpRequest

T = TypeVar("T")
E = TypeVar("E")


class TSessionData(TypedDict):
    cookies: dict[str, str]
    headers: dict[str, str]


class AuthenticatedRequest(HttpRequest):
    user: User


@dataclass
class Success(Generic[T]):
    value: T
    ok: Literal[True] = True


@dataclass
class Failure(Generic[E]):
    err: E
    ok: Literal[False] = False


Result: TypeAlias = Success[E] | Failure[T]  # noqa: UP040


__all__ = ["Result"]


@dataclass
class GSInstructionEntry:
    days_and_times: str
    room: str
    instructor: str
    meeting_dates: str


@dataclass
class GSCourseSection:
    unique_id: str  # gathered from url query param
    number: int
    section_name: str  # eg 60-INT Regular
    url: str
    instruction_mode: str
    status: str
    topic: str
    instruction_entries: list[GSInstructionEntry]


class GSCourse:
    code: str  # eg. CSCI
    level: str  # eg. 331
    title: str  # eg. Database Systems
    sections: list[GSCourseSection]

    def __init__(self, course_full_title: str, course_sections: list[GSCourseSection]):
        self.sections = course_sections

        course_info_re = re.compile(r"^(\w+) *(\w+)? *- *(.+)", flags=re.IGNORECASE)
        match = course_info_re.search(course_full_title)

        if not match:
            raise ValueError(
                f"{course_info_re} did not match course info str: {course_full_title!r}"
            )

        self.code = match.group(1).strip()
        self.level = match.group(2).strip()
        self.title = match.group(3).strip()

    def get_name(self) -> str:
        return f"{self.code} {self.level}"
