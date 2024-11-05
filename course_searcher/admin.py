from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from . import models


@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin[models.School]):
    list_display = ("name", "globalsearch_key", "datetime_created")
    search_fields = ("name", "globalsearch_key")
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin[models.Term]):
    list_display = ("name", "year", "globalsearch_key", "is_available")
    list_filter = ("year", "schools", "is_available")
    search_fields = ("name", "globalsearch_key")
    filter_horizontal = ("schools",)
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.CourseCareer)
class CourseCareerAdmin(admin.ModelAdmin[models.CourseCareer]):
    list_display = ("name",)
    list_filter = ("name", "schools")
    search_fields = ("school__name",)
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin[models.Subject]):
    list_display = ("name", "short_name", "school", "term", "career")
    list_filter = ("school", "term", "career")
    search_fields = ("name", "short_name", "globalsearch_key")
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin[models.Instructor]):
    list_display = ("first_name", "last_name", "datetime_created")
    search_fields = ("first_name", "last_name")
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin[models.Course]):
    list_display = ("level", "title", "career", "school")
    list_filter = ("career", "school")
    search_fields = ("level", "title")
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.CourseClass)
class CourseClassAdmin(admin.ModelAdmin[models.CourseClass]):
    list_display = ("course", "section", "instructor", "status", "instruction_mode", "term")
    list_filter = ("status", "instruction_mode", "term", "course__school")
    search_fields = (
        "section",
        "instructor__first_name",
        "instructor__last_name",
        "course__level",
        "course__title",
    )
    readonly_fields = ("datetime_created", "datetime_modified")
    actions = ["mark_as_open", "mark_as_closed", "mark_as_waitlisted"]

    @admin.action(description="Mark selected classes as open")
    def mark_as_open(self, request: HttpRequest, queryset: QuerySet[models.CourseClass]) -> None:
        queryset.update(status=models.CourseClass.StatusChoices.OPEN)

    @admin.action(description="Mark selected classes as closed")
    def mark_as_closed(self, request: HttpRequest, queryset: QuerySet[models.CourseClass]) -> None:
        queryset.update(status=models.CourseClass.StatusChoices.CLOSED)

    @admin.action(description="Mark selected classes as waitlisted")
    def mark_as_waitlisted(
        self, request: HttpRequest, queryset: QuerySet[models.CourseClass]
    ) -> None:
        queryset.update(status=models.CourseClass.StatusChoices.WAITLISTED)
