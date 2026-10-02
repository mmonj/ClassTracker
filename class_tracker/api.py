from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import ModelSchema, Router

from .models import Course, CourseSection

router = Router(tags=["course sections"])


class CourseSchema(ModelSchema):
    class Meta:
        model = Course
        fields = ("code", "level", "title", "designation")


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
