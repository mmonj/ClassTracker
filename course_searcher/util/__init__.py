from server.util import bulk_create_and_get

from ..global_search.types import GSCourse
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
                unique_fieldnames=["code", "level", "school__id"],
            )
        )
    }
    courses = list(course_name_to_course_map.values())

    for gs_course in gs_courses:
        for gs_course_section in gs_course.sections:
            course = course_name_to_course_map[gs_course.get_name()]
            course_section = CourseSection.from_gs_course_section(gs_course_section, course, term)
            course_section.save()

            instruction_entries = InstructionEntry.entries_from_gs_course_section(
                gs_course_section, course_section, term, name_to_instructor_map
            )

            instruction_entries = list(
                bulk_create_and_get(
                    InstructionEntry,
                    instruction_entries,
                    unique_fieldnames=[
                        "term__id",
                        "course_section__id",
                        "days_and_times",
                        "meeting_dates",
                        "room",
                    ],
                )
            )

            for instruction_entry in instruction_entries:
                instruction_entry.course_section = course_section

    term.courses.add(*courses)

    return courses


def _create_instructors_from_gs_courses(
    gs_courses: list[GSCourse], school: School, term: Term
) -> TNameToInstructorMap:
    instructor_names: set[str] = set()
    for gs_course in gs_courses:
        for course_section in gs_course.sections:
            instructor_names.update(course_section.instructor.split("\n"))

    instructors = [Instructor(name=name, school=school) for name in instructor_names]
    instructors = list(
        bulk_create_and_get(Instructor, instructors, unique_fieldnames=["name", "school__id"])
    )

    return {f.name: f for f in instructors}
