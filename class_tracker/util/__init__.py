import logging

from server.util import atomic_get_or_create, bulk_create_and_get

from ..global_search.typedefs import GSCourse
from ..models import (
    Course,
    CourseCareer,
    CourseSection,
    InstructionEntry,
    Instructor,
    School,
    Subject,
    Term,
)

logger = logging.getLogger("main")

TNameToInstructorMap = dict[str, Instructor]


def create_db_courses(
    gs_courses: list[GSCourse],
    subject: Subject,
    career: CourseCareer,
    school: School,
    term: Term,
) -> list[Course]:
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
