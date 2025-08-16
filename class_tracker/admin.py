from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import (
    ClassAlert,
    ContactInfo,
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
    list_filter = ("schools", "terms", "is_preferred")
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


class ContactInfoInline(admin.TabularInline[ContactInfo, Recipient]):
    model = ContactInfo
    extra = 1
    fields = ("number", "is_enabled")
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

    get_days_and_times.short_description = "Days & Times"  # type: ignore [attr-defined]
    get_start_and_end_dates.short_description = "Start & End Dates"  # type: ignore [attr-defined]
    get_room.short_description = "Location"  # type: ignore [attr-defined]


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin[Recipient]):
    list_display = ("name", "description", "is_contact_by_phone")
    list_filter = ("is_contact_by_phone",)
    search_fields = ("name",)
    filter_horizontal = ("watched_sections",)
    inlines = [ContactInfoInline]

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[Recipient]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "watched_sections__course", "watched_sections__instruction_entries__instructor"
            )
        )

    def watched_sections_display(self, obj: Recipient) -> str:
        sections_info: list[str] = []
        for section in obj.watched_sections.all():
            section_name = f"{section.course.get_name()} - {section.topic}"
            instructors = ", ".join(
                [entry.instructor.name for entry in section.instruction_entries.all()]
            )
            sections_info.append(f"{section_name} (Instructors: {instructors})")
        return "; ".join(sections_info)

    watched_sections_display.short_description = "Watched Sections"  # type: ignore [attr-defined]


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin[ContactInfo]):
    list_display = ("number", "owner", "is_enabled")
    list_filter = ("is_enabled",)
    search_fields = ("number", "owner__name")
    autocomplete_fields = ("owner",)

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[ContactInfo]:
        return super().get_queryset(request).select_related("owner")


@admin.register(ClassAlert)
class ClassAlertAdmin(admin.ModelAdmin[ClassAlert]):
    list_display = ("recipient", "course_section", "datetime_created")
    list_filter = ("recipient", "course_section")
    search_fields = ("recipient__name", "course_section__title")
    raw_id_fields = ("recipient", "course_section")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[ClassAlert]:
        return (
            super()
            .get_queryset(request)
            .select_related("recipient", "course_section", "course_section__course")
        )
