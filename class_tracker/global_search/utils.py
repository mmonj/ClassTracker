from urllib.parse import parse_qs, urlparse

from bs4 import Tag

from .typedefs import GSCourseSection, GSInstructionEntry


def get_course_section(section_attr_elements: list[Tag]) -> GSCourseSection:
    gs_course_section = GSCourseSection(
        unique_id="",
        number=0,
        section_name="",
        topic="",
        url="",
        instruction_mode="",
        status="Closed",
        instruction_entries=[],
    )

    days_and_times_list: list[str] = []
    room_list: list[str] = []
    instructor_list: list[str] = []
    meeting_dates_list: list[str] = []

    for section_attr_element in section_attr_elements:
        assign_section_attributes(
            section_attr_element,
            gs_course_section,
            days_and_times_list,
            room_list,
            instructor_list,
            meeting_dates_list,
        )

    instruction_entries: list[GSInstructionEntry] = []
    if not days_and_times_list or not room_list or not instructor_list or not meeting_dates_list:
        raise ValueError(
            "One of the required lists is empty. Lists values:\n"
            f"days_and_times_list: {days_and_times_list}\n"
            f"room_list: {room_list}\n"
            f"instructor_list: {instructor_list}\n"
            f"meeting_dates_list: {meeting_dates_list}\n"
        )

    base_length = len(days_and_times_list)

    # fill other smaller lists with empty string if they are shorter than the base length
    for item_list in (room_list, instructor_list, meeting_dates_list):
        while len(item_list) < base_length:
            item_list.append("")

    if (
        len(room_list) != base_length
        or len(instructor_list) != base_length
        or len(meeting_dates_list) != base_length
    ):
        raise ValueError(
            "Lists are not of the same length. Lists values:\n"
            f"days_and_times_list: {days_and_times_list}\n"
            f"room_list: {room_list}\n"
            f"instructor_list: {instructor_list}\n"
            f"meeting_dates_list: {meeting_dates_list}\n"
        )

    for days_and_times, room, instructor, meeting_dates in zip(
        days_and_times_list,
        room_list,
        instructor_list,
        meeting_dates_list,
        strict=True,
    ):
        instruction_entry = GSInstructionEntry(
            days_and_times=truncate_if_non_word(days_and_times).strip() or "TBA",
            room=truncate_if_non_word(room).strip() or "TBA",
            instructor=truncate_if_non_word(instructor).strip() or "TBA",
            meeting_dates=truncate_if_non_word(meeting_dates),
        )
        instruction_entries.append(instruction_entry)
    gs_course_section.instruction_entries = instruction_entries

    return gs_course_section


def assign_section_attributes(  # noqa: PLR0912
    section_attr_element: Tag,
    gs_course_section: GSCourseSection,
    days_and_times_list: list[str],
    room_list: list[str],
    instructor_list: list[str],
    meeting_dates_list: list[str],
) -> None:
    data_label = section_attr_element.get("data-label")
    if data_label is None:
        raise ValueError(
            f"Data label is none for section_attr_element:\n\n{str(section_attr_element)[:500]}"
        )

    match data_label:
        case "Class":
            gs_course_section.number = int(section_attr_element.get_text(separator="\n").strip())

            anchor_tag = section_attr_element.select_one("a")
            if anchor_tag is None:
                raise ValueError(f"No anchor tag found in: {section_attr_element}")

            url = anchor_tag.get("href")
            if url is None:
                raise ValueError(f"No href found in anchor tag: {anchor_tag}")
            gs_course_section.url = str(url)

            parsed_url = urlparse(gs_course_section.url)
            query_params = parse_qs(parsed_url.query)
            class_number_searched = query_params.get("class_number_searched", [None])[0]
            if class_number_searched is None:
                raise ValueError(
                    f"url query param 'class_number_searched' is None in url: {gs_course_section.url}"
                )
            gs_course_section.unique_id = class_number_searched

        case "Section":
            gs_course_section.section_name = section_attr_element.get_text(separator="\n").strip()
        case "DaysAndTimes":
            days_and_times_list.extend(
                [
                    line.strip()
                    for line in section_attr_element.get_text(separator="\n").strip().split("\n")
                ]
            )
        case "Room":
            room_list.extend(
                [
                    line.strip()
                    for line in section_attr_element.get_text(separator="\n").strip().split("\n")
                ]
            )
        case "Instructor":
            instructor_list.extend(
                [
                    line.strip()
                    for line in section_attr_element.get_text(separator="\n").strip().split("\n")
                ]
            )
        case "Instruction Mode":
            gs_course_section.instruction_mode = section_attr_element.get_text(
                separator="\n"
            ).strip()
        case "Meeting Dates":
            meeting_dates_list.extend(
                [
                    line.strip()
                    for line in section_attr_element.get_text(separator="\n").strip().split("\n")
                ]
            )
        case "Status":
            status_indicator = section_attr_element.select_one("img[alt][title]")
            if status_indicator is None:
                raise ValueError(
                    f"Status indicator is None for class: {gs_course_section.section_name} - {gs_course_section.number}"
                )
            status = status_indicator.get("title")
            gs_course_section.status = str(status)  # type: ignore[assignment]

        case "Course Topic":
            gs_course_section.topic = section_attr_element.get_text(separator="\n").strip()
        case _:
            raise ValueError(f"Bad data label: '{data_label}'")


def truncate_if_non_word(input_str: str) -> str:
    """
    Truncate string to empty string if there is no word character at all in the string
    """
    if not any(char.isalnum() for char in input_str):
        return ""
    return input_str
