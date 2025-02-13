from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from . import models


@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin[models.School]):
    list_display = ("name", "globalsearch_key", "is_preferred", "datetime_created")
    search_fields = ("name", "globalsearch_key")
    readonly_fields = ("datetime_created", "datetime_modified")

    actions = ["toggle_is_preferred"]

    @admin.action(description="Toggle 'Is Preferred' attribute")
    def toggle_is_preferred(self, _request: HttpRequest, queryset: QuerySet[models.School]) -> None:
        updated_schools: list[models.School] = []
        for school in queryset:
            school.is_preferred = not school.is_preferred
            updated_schools.append(school)

        models.School.objects.bulk_update(updated_schools, fields=["is_preferred"])


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin[models.Term]):
    list_display = ("name", "year", "globalsearch_key", "is_available")
    list_filter = ("year", "schools", "is_available")
    search_fields = ("name", "globalsearch_key")
    filter_horizontal = ("schools",)
    readonly_fields = ("datetime_created", "datetime_modified")

    actions = ["toggle_is_available"]

    @admin.action(description="Toggle 'Is Available' attribute")
    def toggle_is_available(self, _request: HttpRequest, queryset: QuerySet[models.Term]) -> None:
        updated_terms: list[models.Term] = []
        for term in queryset:
            term.is_available = not term.is_available
            updated_terms.append(term)

        models.Term.objects.bulk_update(updated_terms, fields=["is_preferred"])


@admin.register(models.CourseCareer)
class CourseCareerAdmin(admin.ModelAdmin[models.CourseCareer]):
    list_display = ("name", "globalsearch_key")
    list_filter = ("name", "globalsearch_key", "schools")
    search_fields = ("school__name",)
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin[models.Subject]):
    list_display = ("name", "is_preferred")
    list_filter = ("schools",)
    search_fields = ("name", "globalsearch_key")
    readonly_fields = ("datetime_created", "datetime_modified")

    actions = ["toggle_is_preferred"]

    @admin.action(description="Toggle 'Is Preferred' attribute")
    def toggle_is_preferred(
        self, _request: HttpRequest, queryset: QuerySet[models.Subject]
    ) -> None:
        updated_subjects: list[models.Subject] = []
        for subject in queryset:
            subject.is_preferred = not subject.is_preferred
            updated_subjects.append(subject)

        models.Subject.objects.bulk_update(updated_subjects, fields=["is_preferred"])


@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin[models.Instructor]):
    list_display = ("name", "datetime_created")
    search_fields = ("name",)
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin[models.Course]):
    list_display = ("code", "level", "title", "career", "school")
    list_filter = ("career", "school")
    search_fields = ("code", "level", "title")
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.CourseSection)
class CourseSectionAdmin(admin.ModelAdmin[models.CourseSection]):
    list_display = ("course", "section", "status", "instruction_mode", "term")
    list_filter = ("status", "instruction_mode", "term", "course__school")
    search_fields = (
        "section",
        "course__level",
        "course__title",
    )
    readonly_fields = ("datetime_created", "datetime_modified")
    actions = ["mark_as_open", "mark_as_closed", "mark_as_waitlisted"]

    @admin.action(description="Mark selected classes as open")
    def mark_as_open(self, _request: HttpRequest, queryset: QuerySet[models.CourseSection]) -> None:
        queryset.update(status=models.CourseSection.StatusChoices.OPEN)

    @admin.action(description="Mark selected classes as closed")
    def mark_as_closed(
        self, _request: HttpRequest, queryset: QuerySet[models.CourseSection]
    ) -> None:
        queryset.update(status=models.CourseSection.StatusChoices.CLOSED)

    @admin.action(description="Mark selected classes as waitlisted")
    def mark_as_waitlisted(
        self, _request: HttpRequest, queryset: QuerySet[models.CourseSection]
    ) -> None:
        queryset.update(status=models.CourseSection.StatusChoices.WAITLISTED)
