import logging
from datetime import timedelta

from django.utils import timezone

from .global_search.parser import find_open_sections
from .models import ClassAlert, CourseSection, GlobalSettings, Recipient
from .util import (
    SearchGroup,
    get_grouped_watched_sections_for_search,
    group_open_sections_by_recipient,
)
from .util.notifier import notify_recipient

logger = logging.getLogger("main")


def test_job() -> None:
    logger.info("Hello there")


def check_for_open_sections() -> None:
    logger.info("Checking for open sections")

    search_groups = get_grouped_watched_sections_for_search()

    if len(search_groups) == 0:
        logger.info("No recipients with watched sections found")
        return

    logger.info("Found %d search groups to process", len(search_groups))

    all_recipients_with_open_sections: dict[Recipient, list[CourseSection]] = {}

    for group in search_groups:
        group_recipients_with_open_sections = _find_search_group_open_sections(group)

        # merge results with existing data
        for recipient, sections in group_recipients_with_open_sections.items():
            if recipient in all_recipients_with_open_sections:
                all_recipients_with_open_sections[recipient].extend(sections)
            else:
                all_recipients_with_open_sections[recipient] = sections

    if all_recipients_with_open_sections:
        # Filter out sections that have recent alerts within grace period
        filtered_recipients_with_sections = _filter_sections_within_grace_period(
            all_recipients_with_open_sections
        )

        if filtered_recipients_with_sections:
            _notify_recipients(filtered_recipients_with_sections)
        else:
            logger.info("All open sections filtered out due to grace period")
    else:
        logger.info("No open sections found for any recipients")


def _find_search_group_open_sections(group: SearchGroup) -> dict[Recipient, list[CourseSection]]:
    """Process a single search group and return recipients with their open sections."""
    logger.info(
        "Searching for %d sections in %s - %s - %s - %s",
        len(group.section_numbers),
        group.school.name,
        group.term.full_term_name,
        group.subject.name,
        group.career.name,
    )

    try:
        section_num_to_section: dict[int, CourseSection] = {}
        for recipient in group.recipients:
            for watched_section in recipient.watched_sections.all():
                section_num_to_section[watched_section.number] = watched_section

        open_section_numbers = find_open_sections(
            set(group.section_numbers), group.school, group.term, group.subject, group.career
        )

        open_sections = [
            section_num_to_section[num]
            for num in open_section_numbers
            if num in section_num_to_section
        ]

        if len(open_sections) > 0:
            logger.info("Found %d open sections", len(open_sections))
            return group_open_sections_by_recipient(open_sections, group.recipients)

        logger.info("No open sections found for this group")
        return {}

    except (ValueError, ConnectionError, TimeoutError):
        logger.exception(
            "Error searching for classes in %s - %s", group.school.name, group.term.full_term_name
        )
        return {}


def _filter_sections_within_grace_period(
    recipients_with_open_sections: dict[Recipient, list[CourseSection]],
) -> dict[Recipient, list[CourseSection]]:
    """Filter out course sections that have recent ClassAlert records within the grace period."""
    hours_grace_period = 6.0
    try:
        global_settings = GlobalSettings.objects.first()
        if global_settings is not None:
            hours_grace_period = global_settings.hours_renotify_grace_period

        grace_period_cutoff = timezone.now() - timedelta(hours=hours_grace_period)

        # collect all recipients and sections to prepare for bulk query
        all_recipients = list(recipients_with_open_sections.keys())
        all_sections = [
            section
            for sections_list in recipients_with_open_sections.values()
            for section in sections_list
        ]

        recent_alerts = ClassAlert.objects.filter(
            recipient__in=all_recipients,
            course_section__in=all_sections,
            datetime_created__gt=grace_period_cutoff,
        ).select_related("recipient", "course_section")

        # set (recipient_id, section_id) tuples
        recent_alert_pairs = {
            (alert.recipient.id, alert.course_section.id) for alert in recent_alerts
        }

        filtered_recipients_with_sections: dict[Recipient, list[CourseSection]] = {}

        for recipient, open_sections in recipients_with_open_sections.items():
            filtered_sections: list[CourseSection] = []

            for section in open_sections:
                recent_alert_exists = (recipient.id, section.id) in recent_alert_pairs

                if not recent_alert_exists:
                    filtered_sections.append(section)
                else:
                    logger.debug(
                        "Skipping notification for %s - %s %s (recent alert within grace period)",
                        recipient.name,
                        section.course.code,
                        section.course.level,
                    )

            if filtered_sections:
                filtered_recipients_with_sections[recipient] = filtered_sections

        return filtered_recipients_with_sections

    except Exception:
        logger.exception("Error filtering sections within grace period, proceeding without filter")
        return recipients_with_open_sections


def _notify_recipients(recipients_with_open_sections: dict[Recipient, list[CourseSection]]) -> None:
    """Notify all recipients about their open sections and create ClassAlert records."""
    logger.info("Notifying %d recipients about open sections", len(recipients_with_open_sections))

    all_alerts_to_create = [
        ClassAlert(recipient=recipient, course_section=section)
        for recipient, open_sections in recipients_with_open_sections.items()
        for section in open_sections
    ]

    if len(all_alerts_to_create) > 0:
        ClassAlert.objects.bulk_create(all_alerts_to_create)
        logger.info("Created %d ClassAlert records", len(all_alerts_to_create))

    for recipient, open_sections in recipients_with_open_sections.items():
        try:
            course_sections_str = get_formatted_course_sections_msg(open_sections)
            if course_sections_str:
                message = f"Found New Open Course Sections!:\n{course_sections_str}"
                notify_recipient(recipient, message)
                logger.info(
                    "Notified %s about %d open sections", recipient.name, len(open_sections)
                )

        except (ValueError, ConnectionError):
            logger.exception("Error notifying recipient %s", recipient.name)
            continue


def get_formatted_course_sections_msg(course_sections: list[CourseSection]) -> str:
    """
    Each course section will be formatted as: `{course-code} {course-level} - {course_section.topic} ({instructor-names-comma-separated})`
    """
    if len(course_sections) == 0:
        return ""

    formatted_sections: list[str] = []
    for section in course_sections:
        instructor_names: list[str] = [
            instruction_entry.instructor.name
            for instruction_entry in section.instruction_entries.all()
        ]

        # use dict instead of set to preserve order
        unique_instructors = list(dict.fromkeys(instructor_names))
        instructors_str = ", ".join(unique_instructors) if unique_instructors else "TBA"

        formatted_section = (
            f"{section.course.code} {section.course.level} - {section.topic} ({instructors_str})"
        )
        formatted_sections.append(formatted_section)

    return "\n".join(formatted_sections)
