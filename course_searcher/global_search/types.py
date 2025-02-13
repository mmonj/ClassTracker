import re
from dataclasses import dataclass
from typing import Generic, Literal, TypeAlias, TypeVar
from urllib.parse import parse_qs, urlparse

from bs4 import Tag

T = TypeVar("T")
E = TypeVar("E")


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


class GSCourseSection:
    unique_id: str  # gathered from url query param
    number: str
    section_name: str
    days_and_times: str
    room: str
    instructor: str  # could be Bryan Nevarez\nAdam Kapelner\nAdam Kapelner
    instruction_mode: str
    meeting_dates: str
    status: str
    topic: str
    url: str

    def __init__(self, class_attribute_elms: list[Tag]):
        for class_attribute_elm in class_attribute_elms:
            self._assign_attribute(class_attribute_elm)

    def _assign_attribute(self, section_attr_element: Tag) -> None:  # noqa: PLR0912
        data_label = section_attr_element.get("data-label")
        if data_label is None:
            raise ValueError(
                f"Data label is none for section_attr_element:\n\n{str(section_attr_element)[:500]}"
            )

        match data_label:
            case "Class":
                self.number = section_attr_element.get_text(separator="\n").strip()

                anchor_tag = section_attr_element.select_one("a")
                if anchor_tag is None:
                    raise ValueError(f"No anchor tag found in: {section_attr_element}")
                url = anchor_tag.get("href")
                if url is None:
                    raise ValueError(f"No href found in anchor tag: {anchor_tag}")
                self.url = str(url)

                parsed_url = urlparse(self.url)
                query_params = parse_qs(parsed_url.query)
                class_number_searched = query_params.get("class_number_searched", [None])[0]
                if class_number_searched is None:
                    raise ValueError(
                        f"url query param 'class_number_searched' is None in url: {self.url}"
                    )
                self.unique_id = class_number_searched

            case "Section":
                self.section_name = section_attr_element.get_text(separator="\n").strip()
            case "DaysAndTimes":
                self.days_and_times = section_attr_element.get_text(separator="\n").strip()
            case "Room":
                self.room = section_attr_element.get_text(separator="\n").strip()
            case "Instructor":
                self.instructor = section_attr_element.get_text(separator="\n").strip()
            case "Instruction Mode":
                self.instruction_mode = section_attr_element.get_text(separator="\n").strip()
            case "Meeting Dates":
                self.meeting_dates = section_attr_element.get_text(separator="\n").strip()
            case "Status":
                status_indicator = section_attr_element.select_one("img[alt][title]")
                if status_indicator is None:
                    raise ValueError(
                        f"Status indicator is None for class: {self.section_name} - {self.number}"
                    )
                status = status_indicator.get("title")
                self.status = str(status)

            case "Course Topic":
                self.topic = section_attr_element.get_text(separator="\n").strip()
            case _:
                raise ValueError(f"Bad data label: '{data_label}'")


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
