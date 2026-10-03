from django.db.models import F, QuerySet
from django.http import HttpRequest
from ninja import ModelSchema, Router
from ninja.errors import HttpError

from .models import Course, CourseSection

router = Router(tags=["course sections"])


class CourseSchema(ModelSchema):
    class Meta:
        model = Course
        fields = ("prefix", "level", "title", "designation")


class CourseSectionSchema(ModelSchema):
    course: CourseSchema

    class Meta:
        model = CourseSection
        fields = ("number", "section", "topic", "instruction_mode")


@router.get("/course-sections/", response=list[CourseSectionSchema])
def get_course_sections(
    request: HttpRequest,  # noqa: ARG001
    term_code: int,
    school_code: str,
    class_number: int,
) -> QuerySet[CourseSection]:
    # a class number is not guaranteed to be unique within a term and school
    return (
        CourseSection.objects.filter(
            term__globalsearch_key=str(term_code),
            course__school__globalsearch_key=school_code.upper(),
            number=class_number,
        )
        .select_related("course")
        .order_by("id")
    )


@router.get("/course-sections/variable-topic/", response=list[CourseSectionSchema])
def get_variable_topic_sections(
    request: HttpRequest,  # noqa: ARG001
    term_code: int,
    school_code: str,
    course_prefix: str | None = None,
    course_level: str | None = None,
) -> QuerySet[CourseSection]:
    # an empty value is treated the same as an omitted one
    if course_level and not course_prefix:
        raise HttpError(422, "course_prefix is required when course_level is provided")

    variable_topic_sections = (
        CourseSection.objects.filter(
            term__globalsearch_key=str(term_code),
            course__school__globalsearch_key=school_code.upper(),
        )
        .exclude(topic__iexact=F("course__title"))
        .select_related("course")
        .order_by("course__prefix", "course__level", "section", "id")
    )

    if course_prefix:
        variable_topic_sections = variable_topic_sections.filter(course__prefix=course_prefix.upper())
    if course_level:
        # Course.level keeps any designation suffix (eg. "101W"), so no splitting is needed
        variable_topic_sections = variable_topic_sections.filter(course__level=course_level.upper())

    return variable_topic_sections
