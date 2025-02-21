from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import (
    Course,
    CourseCareer,
    CourseSection,
    InstructionEntry,
    Instructor,
    School,
    Subject,
    Term,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin[School]):
    list_display = ("name", "globalsearch_key", "is_preferred", "datetime_created")
    search_fields = ("name", "globalsearch_key")
    readonly_fields = ("datetime_created", "datetime_modified")
    list_filter = ("is_preferred",)
    ordering = ("name",)

    actions = ["toggle_is_preferred"]

    @admin.action(description="Toggle 'Is Preferred' attribute")
    def toggle_is_preferred(self, _request: HttpRequest, queryset: QuerySet[School]) -> None:
        queryset.update(is_preferred=~models.F("is_preferred"))


@admin.register(Term)
class TermAdmin(admin.ModelAdmin[Term]):
    list_display = ("name", "year", "globalsearch_key", "is_available", "is_preferred")
    list_filter = ("year", "schools", "is_available", "is_preferred")
    search_fields = ("name", "globalsearch_key")
    filter_horizontal = ("schools",)
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("-year", "name")

    actions = ["toggle_is_available", "toggle_is_preferred"]

    @admin.action(description="Toggle 'Is Available' attribute")
    def toggle_is_available(self, _request: HttpRequest, queryset: QuerySet[Term]) -> None:
        queryset.update(is_available=~models.F("is_available"))

    @admin.action(description="Toggle 'Is Preferred' attribute")
    def toggle_is_preferred(self, _request: HttpRequest, queryset: QuerySet[Term]) -> None:
        queryset.update(is_preferred=~models.F("is_preferred"))


@admin.register(CourseCareer)
class CourseCareerAdmin(admin.ModelAdmin[CourseCareer]):
    list_display = ("name", "globalsearch_key", "is_preferred")
    list_filter = ("name", "globalsearch_key", "schools", "terms", "is_preferred")
    search_fields = ("name", "globalsearch_key")
    filter_horizontal = ("schools", "terms")
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin[Subject]):
    list_display = ("name", "globalsearch_key", "is_preferred")
    list_filter = ("schools", "is_preferred")
    search_fields = ("name", "globalsearch_key")
    filter_horizontal = ("schools", "terms")
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("name",)

    actions = ["toggle_is_preferred"]

    @admin.action(description="Toggle 'Is Preferred' attribute")
    def toggle_is_preferred(self, _request: HttpRequest, queryset: QuerySet[Subject]) -> None:
        queryset.update(is_preferred=~models.F("is_preferred"))


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin[Instructor]):
    list_display = ("name", "school", "datetime_created")
    list_filter = ("school", "terms")
    search_fields = ("name",)
    filter_horizontal = ("terms",)
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin[Course]):
    list_display = ("code", "level", "title", "career", "school")
    list_filter = ("career", "school", "terms")
    search_fields = ("code", "level", "title")
    filter_horizontal = ("terms",)
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("code", "level")


class InstructionEntryInline(admin.TabularInline[InstructionEntry, CourseSection]):
    model = InstructionEntry
    extra = 1
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin[CourseSection]):
    list_display = ("course", "section", "status", "instruction_mode", "term")
    list_filter = ("status", "instruction_mode", "term", "course__school")
    search_fields = ("section", "course__level", "course__title")
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("course", "section")

    inlines = [InstructionEntryInline]

    actions = ["mark_as_open", "mark_as_closed", "mark_as_waitlisted"]

    @admin.action(description="Mark selected classes as open")
    def mark_as_open(self, _request: HttpRequest, queryset: QuerySet[CourseSection]) -> None:
        queryset.update(status=CourseSection.StatusChoices.OPEN)

    @admin.action(description="Mark selected classes as closed")
    def mark_as_closed(self, _request: HttpRequest, queryset: QuerySet[CourseSection]) -> None:
        queryset.update(status=CourseSection.StatusChoices.CLOSED)

    @admin.action(description="Mark selected classes as waitlisted")
    def mark_as_waitlisted(self, _request: HttpRequest, queryset: QuerySet[CourseSection]) -> None:
        queryset.update(status=CourseSection.StatusChoices.WAITLISTED)


@admin.register(InstructionEntry)
class InstructionEntryAdmin(admin.ModelAdmin[InstructionEntry]):
    list_display = (
        "instructor",
        "course_section",
        "get_days_and_times",
        "get_start_and_end_dates",
        "get_room",
        "term",
    )
    list_filter = ("term", "course_section__course", "instructor")
    search_fields = ("instructor__name", "course_section__course__title", "room")
    readonly_fields = ("datetime_created", "datetime_modified")
    ordering = ("course_section", "instructor")

    def get_days_and_times(self, obj: InstructionEntry) -> str:
        return obj.get_days_and_times()

    def get_start_and_end_dates(self, obj: InstructionEntry) -> str:
        return obj.get_start_and_end_dates()

    def get_room(self, obj: InstructionEntry) -> str:
        return f"{obj.building} {obj.room}"
