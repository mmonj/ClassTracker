import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from server.util import atomic_get_or_create, bulk_create_and_get

from ..global_search.typedefs import GSCourse
from ..models import (
    Course,
    CourseCareer,
    CourseSection,
    InstructionEntry,
    Instructor,
    Recipient,
    School,
    Subject,
    Term,
)

logger = logging.getLogger("main")

TNameToInstructorMap = dict[str, Instructor]
TSearchGroupKey = tuple[School, Term, Subject, CourseCareer]


@dataclass
class SearchGroup:
    school: School
    term: Term
    subject: Subject
    career: CourseCareer
    section_numbers: list[int]
    recipients: list[Recipient]


def get_grouped_watched_sections_for_search() -> list[SearchGroup]:
    """
    Group recipients watched sections by (school, term, subject, career)
    to minimize the number of calls to `search_for_classes`
    """
    from class_tracker.models import Recipient

    search_groups: defaultdict[TSearchGroupKey, dict[str, Any]] = defaultdict(
        lambda: {"section_numbers": set(), "recipients": set()}
    )

    for recipient in Recipient.objects.prefetch_related(
        "watched_sections__course__school",
        "watched_sections__course__subject",
        "watched_sections__course__career",
        "watched_sections__term",
    ).all():
        for section in recipient.watched_sections.all():
            course = section.course
            key = (course.school, section.term, course.subject, course.career)

            search_groups[key]["section_numbers"].add(section.number)
            search_groups[key]["recipients"].add(recipient)

    results: list[SearchGroup] = []
    for key, data in search_groups.items():
        school, term, subject, career = key
        search_group = SearchGroup(
            school=school,
            term=term,
            subject=subject,
            career=career,
            section_numbers=list(data["section_numbers"]),
            recipients=list(data["recipients"]),
        )
        results.append(search_group)

    return results


def group_open_sections_by_recipient(
    open_sections: list[CourseSection], recipients: list[Recipient]
) -> dict[Recipient, list[CourseSection]]:
    recipient_to_sections = defaultdict(list)

    open_section_numbers: set[int] = {section.number for section in open_sections}

    for recipient in recipients:
        for watched_section in recipient.watched_sections.all():
            if watched_section.number in open_section_numbers:
                # find the actual open section object
                matching_open_section = next(
                    (
                        section
                        for section in open_sections
                        if section.number == watched_section.number
                    ),
                    None,
                )
                if matching_open_section:
                    recipient_to_sections[recipient].append(matching_open_section)

    return dict(recipient_to_sections)


def create_db_courses(
    gs_courses: list[GSCourse],
    subject: Subject,
    career: CourseCareer,
    school: School,
    term: Term,
) -> list[Course]:
    logger.info(
        " - Creating %s database courses for %s (%s) - %s, %s",
        len(gs_courses),
        school.name,
        term.name,
        career.name,
        subject.name,
    )
    name_to_instructor_map = _create_instructors_from_gs_courses(gs_courses, school, term)

    course_name_to_course_map = {
        course.get_name(): course
        for course in list(
            bulk_create_and_get(
                Course,
                [Course.from_gs_course(c, subject, career, school) for c in gs_courses],
                fields=["code", "level", "school__id"],
            )
        )
    }

    courses = list(course_name_to_course_map.values())

    for gs_course in gs_courses:
        for gs_course_section in gs_course.sections:
            course = course_name_to_course_map[gs_course.get_name()]
            course_section = CourseSection.from_gs_course_section(gs_course_section, course, term)
            course_section, _ = atomic_get_or_create(course_section, fields=["gs_unique_id"])

            InstructionEntry.objects.filter(course_section=course_section).delete()

            InstructionEntry.create_entries_from_gs_course_section(
                gs_course_section, course_section, term, name_to_instructor_map
            )

    term.courses.add(*courses)

    return courses


def _create_instructors_from_gs_courses(
    gs_courses: list[GSCourse], school: School, term: Term
) -> TNameToInstructorMap:
    instructor_names: set[str] = set()
    for gs_course in gs_courses:
        for course_section in gs_course.sections:
            for instruction_entry in course_section.instruction_entries:
                if instruction_entry.instructor:
                    instructor_names.add(instruction_entry.instructor)

    instructors = [Instructor(name=name, school=school) for name in instructor_names]
    instructors = list(bulk_create_and_get(Instructor, instructors, fields=["name", "school__id"]))

    term.instructors.add(*instructors)

    return {f.name: f for f in instructors}
