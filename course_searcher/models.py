import datetime
import re

import pytz
from django.db import models

from .global_search.types import GSCourse, GSCourseSection

TTermName = str
TTermYear = int

BuildingName = str
RoomNumber = str

NYC_TZ = pytz.timezone("America/New_York")


class CommonModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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

    @property
    def full_term_name(self) -> str:
        return f"{self.year} {self.name}"

    def __repr__(self) -> str:
        return f"<Term(id={self.id}, name='{self.name}', year={self.year}, is_available={self.is_available})>"

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
    ) -> "Course":
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

    gs_unique_id = models.CharField(max_length=100, blank=False, unique=True)
    topic = models.CharField(max_length=200, blank=False)
    url = models.CharField(max_length=1000, blank=False)
    section = models.CharField(max_length=20, blank=False)  # eg "121-LEC Regular"
    instruction_mode = models.CharField(max_length=50)  # eg. in person, hybrid
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="classes")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="classes")

    class Meta:
        verbose_name_plural = "Course Sections"
        ordering = ("course", "section")

    def __str__(self) -> str:
        instruction_entries = self.instruction_entries.all()
        if len(instruction_entries) == 0:
            return f"{self.course.level} {self.section} - {instruction_entries[0]}"
        return f"{self.course.level} {self.section} - {len(instruction_entries)} instructors"

    def __repr__(self) -> str:
        return f"<CourseSection(id={self.id}, section='{self.section}', status='{self.status}', instruction mode='{self.instruction_mode}')>"

    @classmethod
    def from_gs_course_section(
        cls, gs_course_section: GSCourseSection, course: Course, term: Term
    ) -> "CourseSection":
        instance = cls(
            gs_unique_id=gs_course_section.unique_id,
            topic=gs_course_section.topic,
            url=gs_course_section.url,
            section=gs_course_section.section_name,
            instruction_mode=gs_course_section.instruction_mode,
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
    start_time = models.TimeField()  # eg. 10:45AM
    end_time = models.TimeField()  # eg. 12:00PM

    building = models.CharField(max_length=100)  # Extracted from `room`
    room_number = models.CharField(max_length=20)  # Extracted from `room`
    floor_number = models.CharField(max_length=20)

    start_date = models.DateField()
    end_date = models.DateField()

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
            "room_number",
        )

    def __str__(self) -> str:
        days_display = ", ".join(day.get_name_display() for day in self.days.all())
        return f"{days_display} {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')} in {self.building} {self.room_number}"

    def __repr__(self) -> str:
        days_display = ", ".join(day.get_name_display() for day in self.days.all())
        return f"<InstructionEntry(id={self.id}, days='{days_display}', start_time={self.start_time.strftime('%I:%M %p')}, end_time={self.end_time.strftime('%I:%M %p')}, building='{self.building}', room_number='{self.room_number}')>"

    @staticmethod
    def parse_days(days_str: str) -> list[Day]:
        """Convert a string like 'TuTh' into a list of Day objects."""
        day_mapping = {d.value: d for d in Day.DayChoices}
        return [
            Day.objects.get_or_create(name=day_mapping[abbr])[0]
            for abbr in [days_str[i : i + 2] for i in range(0, len(days_str), 2)]
        ]

    @staticmethod
    def parse_meeting_dates(meeting_dates: str) -> tuple[datetime.date, datetime.date]:
        """Convert '01/25/2025 - 05/22/2025' into (start_date, end_date) and adjust to NYC timezone."""
        start_str, end_str = meeting_dates.split(" - ")

        start_naive = datetime.datetime.strptime(start_str, "%m/%d/%Y")  # noqa: DTZ007
        end_naive = datetime.datetime.strptime(end_str, "%m/%d/%Y")  # noqa: DTZ007

        start_nyc = NYC_TZ.localize(start_naive)
        end_nyc = NYC_TZ.localize(end_naive)

        return start_nyc.date(), end_nyc.date()

    @staticmethod
    def parse_room(room_str: str) -> tuple[BuildingName, RoomNumber]:
        """Convert strings like 'Kiely Hall 258' into ('Kiely Hall', '258')."""
        parts = room_str.rsplit(" ", 1)
        if len(parts) > 1:
            return (parts[0], parts[1])
        raise ValueError(f"No space found in {room_str} to separate building and room number")

    @staticmethod
    def parse_floor_number(room_number: str) -> str:
        floor_number_re = re.compile("[a-z]*(0-9)", flags=re.IGNORECASE)
        match = floor_number_re.match(room_number)

        if match is None:
            raise ValueError(f"{room_number} has no floor number")

        return match.group(1)

    @staticmethod
    def parse_days_and_times(
        days_and_times: str,
    ) -> tuple[list[Day], datetime.time, datetime.time]:
        """Convert 'TuTh 5:00PM - 5:30PM' into a tuple of ([listDay], start_time, end_time) using NYC as the timezone"""
        parts = days_and_times.split()
        days_part = parts[0]  # eg. yields 'TuTh'
        time_part = parts[1:]  # eg yields ['5:00PM', '-', '5:30PM']

        start_time_naive = datetime.datetime.strptime(time_part[0], "%I:%M%p")  # noqa: DTZ007
        end_time_naive = datetime.datetime.strptime(time_part[2], "%I:%M%p")  # noqa: DTZ007

        start_time_nyc = NYC_TZ.localize(start_time_naive)
        end_time_nyc = NYC_TZ.localize(end_time_naive)

        start_time = start_time_nyc.time()
        end_time = end_time_nyc.time()

        days = InstructionEntry.parse_days(days_part)

        return days, start_time, end_time

    @staticmethod
    def entries_from_gs_course_section(
        gs_course_section: GSCourseSection,
        course_section: CourseSection,
        term: Term,
        name_to_instructors_map: dict[str, Instructor],
    ) -> list["InstructionEntry"]:
        instruction_entries: list[InstructionEntry] = []

        for days_and_times, room, instructor_name, meeting_dates in zip(
            gs_course_section.days_and_times.split("\n"),
            gs_course_section.room.split("\n"),
            gs_course_section.instructor.split("\n"),
            gs_course_section.meeting_dates.split("\n"),
            strict=True,
        ):
            days, start_time, end_time = InstructionEntry.parse_days_and_times(days_and_times)
            start_date, end_date = InstructionEntry.parse_meeting_dates(meeting_dates)
            building, room_number = InstructionEntry.parse_room(room)
            floor_number = InstructionEntry.parse_floor_number(room_number)

            instruction_entry = InstructionEntry.objects.create(
                start_time=start_time,
                end_time=end_time,
                start_date=start_date,
                end_date=end_date,
                building=building,
                room_number=room_number,
                floor_number=floor_number,
                instructor=name_to_instructors_map[instructor_name],
                course_section=course_section,
                term=term,
            )

            instruction_entry.days.set(days)
            instruction_entries.append(instruction_entry)

        return instruction_entries
