import datetime
import re
import sys
from typing import Any, NamedTuple, Self

import pytz
from django.db import models

from .global_search.typedefs import GSCourse, GSCourseSection

TTermName = str
TTermYear = int

TBuildingName = str
TRoom = str
TFloorNumber = str

NYC_TZ = pytz.timezone("America/New_York")


class InstructorInfo(NamedTuple):
    name: str
    days_times: str


class CommonModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        # include datetime_modified if not provided
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = list(update_fields)
            if "datetime_modified" not in update_fields:
                update_fields.append("datetime_modified")
                kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)


class School(CommonModel):
    name = models.CharField(max_length=100)
    globalsearch_key = models.CharField(max_length=100, unique=True)
    is_preferred = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<School(id={self.id}, name='{self.name}', globalsearch_key='{self.globalsearch_key}', is_preferred={self.is_preferred})>"


class Term(CommonModel):
    name = models.CharField(max_length=100)  # eg. Spring Term
    globalsearch_key = models.CharField(max_length=100, unique=True)
    year = models.IntegerField(blank=False)
    is_available = models.BooleanField(default=False)
    is_preferred = models.BooleanField(default=False)

    schools = models.ManyToManyField(School, related_name="terms")

    class Meta:
        unique_together = ("name", "year")

    def __str__(self) -> str:
        return f"{self.year} {self.name}"

    def __repr__(self) -> str:
        return f"<Term(id={self.id}, name='{self.name}', year={self.year}, is_available={self.is_available})>"

    @property
    def full_term_name(self) -> str:
        return f"{self.year} {self.name}"

    @staticmethod
    def get_term_name_and_year(
        full_term_name: str,
    ) -> tuple[TTermName, TTermYear] | tuple[None, None]:
        term_year_regex = r" *(\d+) *(.+)"

        term_year_name_match = re.match(term_year_regex, full_term_name)
        if term_year_name_match is None:
            return None, None

        return term_year_name_match.group(2).strip(), int(term_year_name_match.group(1).strip())


class CourseCareer(CommonModel):
    name = models.CharField(max_length=50)  # eg Undergraduate
    globalsearch_key = models.CharField(max_length=50, unique=True)  # eg UGRD
    is_preferred = models.BooleanField(default=False)

    terms = models.ManyToManyField(Term, related_name="careers")
    schools = models.ManyToManyField(School, related_name="careers")

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<CourseCareer(id={self.id}, name='{self.name}', globalsearch_key='{self.globalsearch_key}')>"


class Subject(CommonModel):
    name = models.CharField(max_length=100)  # eg Computer Science
    globalsearch_key = models.TextField(max_length=100, unique=True)  # eg. CMSC (comp sci)
    is_preferred = models.BooleanField(default=False)

    terms = models.ManyToManyField(Term, related_name="subjects")
    schools = models.ManyToManyField(School, related_name="subjects")

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}', globalsearch_key='{self.globalsearch_key}')>"


class Course(CommonModel):
    # custom shortname (eg. CSCI, MAC, MATH), not associated with globalsearch_key (such as CMSC)
    code = models.CharField(max_length=100, default="", verbose_name="Course Code")
    level = models.CharField(max_length=10, default="")  # eg. "316"
    title = models.CharField(max_length=100)  # eg. "Principles of Programming Lang"
    designation = models.CharField(max_length=10, default="")  # eg. W (writing-intensive)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    career = models.ForeignKey(CourseCareer, on_delete=models.CASCADE, related_name="courses")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    terms = models.ManyToManyField(Term, related_name="courses")

    class Meta:
        unique_together = ("code", "level", "school")

    def __str__(self) -> str:
        return f"{self.level} - {self.title}"

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code='{self.code}', level='{self.level}', title='{self.title}')>"

    def get_name(self) -> str:
        return f"{self.code} {self.level}"

    @classmethod
    def from_gs_course(
        cls, gs_course: GSCourse, subject: Subject, career: CourseCareer, school: School
    ) -> Self:
        course = cls(
            code=gs_course.code,
            level=gs_course.level,
            title=gs_course.title,
            designation="W" if gs_course.level.endswith("W") else "",
        )
        course.subject = subject
        course.career = career
        course.school = school

        return course


class CourseSection(CommonModel):
    class StatusChoices(models.TextChoices):
        OPEN = ("open", "Open")
        CLOSED = ("closed", "Closed")
        WAITLISTED = ("waitlisted", "Waitlisted")

    gs_unique_id = models.CharField(max_length=100, blank=False, unique=True)  # found in url
    number = models.IntegerField(blank=False)  # eg. class number 43070
    section = models.CharField(max_length=20, blank=False)  # eg "121-LEC Regular"
    topic = models.CharField(max_length=200, blank=False)
    url = models.CharField(max_length=1000, blank=False)
    instruction_mode = models.CharField(max_length=50)  # eg. in person, hybrid
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="sections")

    class Meta:
        verbose_name_plural = "Course Sections"
        ordering = ("course", "section")
        unique_together = ("term", "number")

    def __str__(self) -> str:
        instruction_entries = self.instruction_entries.all()
        if len(instruction_entries) == 0:
            return (
                f"{self.number}: {self.course.code} {self.course.level} - {instruction_entries[0]}"
            )
        return f"{self.number}: {self.course.code} {self.course.level} - {len(instruction_entries)} instructors"

    def __repr__(self) -> str:
        return f"<CourseSection(id={self.id}, section='{self.section}', status='{self.status}', instruction mode='{self.instruction_mode}')>"

    @property
    def instruction_list(self) -> list[InstructorInfo]:
        entries = self.instruction_entries.all()
        seen: set[tuple[str, str]] = set()
        result: list[InstructorInfo] = []

        for entry in entries:
            name = entry.instructor.name
            days_times = entry.get_days_and_times()
            key = (name, days_times)
            if key not in seen:
                seen.add(key)
                result.append(InstructorInfo(name=name, days_times=days_times))
        return result

    @classmethod
    def from_gs_course_section(
        cls, gs_course_section: GSCourseSection, course: Course, term: Term
    ) -> Self:
        instance = cls(
            gs_unique_id=gs_course_section.unique_id,
            number=gs_course_section.number,
            section=gs_course_section.section_name,
            instruction_mode=gs_course_section.instruction_mode,
            url=gs_course_section.url,
            topic=gs_course_section.topic,
        )
        instance.course = course
        instance.term = term

        return instance


class Instructor(CommonModel):
    name = models.CharField(max_length=100)

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="instructors")
    terms = models.ManyToManyField(Term, related_name="instructors")

    class Meta:
        unique_together = ("name", "school")

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<Instructor(id={self.id}, full_name='{self.name}')>"


class Day(models.Model):
    class DayChoices(models.TextChoices):
        MONDAY = ("Mo", "Monday")
        TUESDAY = ("Tu", "Tuesday")
        WEDNESDAY = ("We", "Wednesday")
        THURSDAY = ("Th", "Thursday")
        FRIDAY = ("Fr", "Friday")
        SATURDAY = ("Sa", "Saturday")
        SUNDAY = ("Su", "Sunday")

    name = models.CharField(max_length=10, choices=DayChoices.choices, unique=True)

    def __str__(self) -> str:
        return self.get_name_display()

    def __repr__(self) -> str:
        return f"<Day(id={self.id}, name='{self.get_name_display()}')>"


class InstructionEntry(CommonModel):
    days = models.ManyToManyField(Day, related_name="instruction_entries")
    start_time = models.TimeField(null=True)  # eg. 10:45AM; `null=True` due to TBA designation
    end_time = models.TimeField(null=True)  # eg. 12:00PM; `null=True` due to TBA designation

    building = models.CharField(max_length=100)  # Extracted from `location`
    room = models.CharField(max_length=20)  # Extracted from `location`
    floor_number = models.CharField(max_length=20)

    start_date = models.DateField(null=True)  # `null=True` due to '-' designation
    end_date = models.DateField(null=True)  # `null=True` due to '-' designation

    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    course_section = models.ForeignKey(
        CourseSection, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="instruction_entries")

    class Meta:
        unique_together = (
            "term",
            "course_section",
            "start_time",
            "end_time",
            "start_date",
            "end_date",
            "building",
            "room",
            "instructor",
        )

    def __str__(self) -> str:
        return f"Times: {self.get_days_and_times()}; location: {self.location}"

    def __repr__(self) -> str:
        days_display = ", ".join(day.get_name_display() for day in self.days.all())
        return f"<InstructionEntry(id={self.id}, days='{days_display}', start_time={self._get_time_str(self.start_time)}, end_time={self._get_time_str(self.end_time)}, building='{self.building}', room_number='{self.room}')>"

    def get_days_and_times(self) -> str:
        """Get string like 'Tu, Thu 10:45AM - 12:00PM'"""
        days: models.QuerySet[Day] = self.days.all()
        days_display = ", ".join(day.name for day in days)

        start_time = self._get_time_str(self.start_time)
        end_time = self._get_time_str(self.end_time)

        if start_time is None or end_time is None:
            return "TBA"

        return f"{days_display} {start_time} - {end_time}"

    def get_start_and_end_dates(self) -> str:
        """Get string like '01/25/2025 - 05/22/2025'"""
        if self.start_date is None or self.end_date is None:
            return "-"
        return f"{self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}"

    def _get_time_str(self, time: datetime.time | None) -> str | None:
        return (time and time.strftime("%I:%M %p")) or None

    @property
    def location(self) -> str:
        return self.building + self.room

    @staticmethod
    def parse_days(days_str: str) -> list[Day]:
        """Convert a string like 'TuTh' into a list of Day objects."""
        day_mapping = {d.value: d for d in Day.DayChoices}  # type: ignore[misc]
        return [
            Day.objects.get_or_create(name=day_mapping[abbr])[0]
            for abbr in [days_str[i : i + 2] for i in range(0, len(days_str), 2)]
        ]

    @staticmethod
    def parse_meeting_dates(
        meeting_dates: str,
    ) -> tuple[datetime.date | None, datetime.date | None]:
        """Convert '01/25/2025 - 05/22/2025' into (start_date, end_date) and adjust to NYC timezone."""
        parts = meeting_dates.split(" - ")
        num_expected_values = 2

        if len(parts) > num_expected_values:
            raise ValueError(f"Unexpected value: {meeting_dates=}")

        if len(parts) != num_expected_values:
            return (None, None)

        start_str, end_str = parts

        start_naive = datetime.datetime.strptime(start_str, "%m/%d/%Y")  # noqa: DTZ007
        end_naive = datetime.datetime.strptime(end_str, "%m/%d/%Y")  # noqa: DTZ007

        start_nyc = NYC_TZ.localize(start_naive)
        end_nyc = NYC_TZ.localize(end_naive)

        return start_nyc.date(), end_nyc.date()

    @staticmethod
    def parse_location(location: str) -> tuple[TBuildingName, TRoom, TFloorNumber]:
        """Decompose strings like 'Kiely Hall 258' into ('Kiely Hall', '258', '2')."""
        if not location:
            return "", "", ""

        # split by the last space to separate building and room
        # assumes the last part is the room number
        parts = location.rsplit(" ", 1)
        if len(parts) == 1:
            return "", location, ""

        floor_number_re = re.compile(r"\b[a-z]*([0-9]{1,2})[0-9]{2,}$", flags=re.IGNORECASE)
        match = floor_number_re.match(location)

        # if no trailing numbers found, like with 'Online Synchronous'
        if not match:
            return "", location, ""

        return parts[0], parts[1], match.group(1)

    @staticmethod
    def parse_days_and_times(
        days_and_times: str,
    ) -> tuple[list[Day], datetime.time | None, datetime.time | None]:
        """Convert 'TuTh 5:00PM - 5:30PM' into a tuple of (list[Day], start_time, end_time) using NYC as the timezone"""
        print(f"Parsing days and times: {days_and_times=}", file=sys.stderr)

        parts = days_and_times.split()
        if len(parts) == 1:
            return ([], None, None)

        days_part = parts[0]  # eg. yields 'TuTh'
        time_part = parts[1:]  # eg yields ['5:00PM', '-', '5:30PM']

        if len(time_part) != 3 or time_part[1] != "-":  # noqa: PLR2004
            return ([], None, None)

        start_time_naive = datetime.datetime.strptime(time_part[0], "%I:%M%p")  # noqa: DTZ007
        end_time_naive = datetime.datetime.strptime(time_part[2], "%I:%M%p")  # noqa: DTZ007

        start_time_nyc = NYC_TZ.localize(start_time_naive)
        end_time_nyc = NYC_TZ.localize(end_time_naive)

        start_time = start_time_nyc.time()
        end_time = end_time_nyc.time()

        days = InstructionEntry.parse_days(days_part)

        return days, start_time, end_time

    @staticmethod
    def create_entries_from_gs_course_section(
        gs_course_section: GSCourseSection,
        course_section: CourseSection,
        term: Term,
        name_to_instructors_map: dict[str, Instructor],
    ) -> list["InstructionEntry"]:
        instruction_entries: list[InstructionEntry] = []
        for gs_instruction_entry in gs_course_section.instruction_entries:
            days, start_time, end_time = InstructionEntry.parse_days_and_times(
                gs_instruction_entry.days_and_times
            )
            start_date, end_date = InstructionEntry.parse_meeting_dates(
                gs_instruction_entry.meeting_dates
            )
            building, room, floor_number = InstructionEntry.parse_location(
                gs_instruction_entry.room
            )

            instruction_entry, _ = InstructionEntry.objects.get_or_create(
                start_time=start_time,
                end_time=end_time,
                start_date=start_date,
                end_date=end_date,
                building=building,
                room=room,
                floor_number=floor_number,
                instructor=name_to_instructors_map[gs_instruction_entry.instructor],
                course_section=course_section,
                term=term,
            )

            instruction_entry.days.set(days)
            instruction_entries.append(instruction_entry)

        return instruction_entries


class Recipient(CommonModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_contact_by_phone = models.BooleanField(default=True)
    watched_sections = models.ManyToManyField(CourseSection, related_name="watched_by", blank=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Recipient(id={self.id}, name={self.name!r})>"


class ContactInfo(CommonModel):
    number = models.CharField(max_length=20, unique=True, db_index=True)
    owner = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="phone_numbers")
    is_enabled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.number} ({'Preferred' if self.is_enabled else 'Secondary'})"

    def __repr__(self) -> str:
        return f"<ContactInfo(id={self.id}, number={self.number!r}, owner_id={self.owner_id})>"


class ClassAlert(CommonModel):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="alerts")
    course_section = models.ForeignKey(
        CourseSection, on_delete=models.CASCADE, related_name="alerts"
    )

    class Meta:
        unique_together = ("recipient", "course_section", "datetime_created")
        indexes = [models.Index(fields=["recipient", "course_section"])]

    def __str__(self) -> str:
        return f"Alert for {self.recipient.name} on {self.course_section}"

    def __repr__(self) -> str:
        return f"<ClassAlert(id={self.id}, recipient_id={self.recipient_id}, course_section_id={self.course_section_id})>"
