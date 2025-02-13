import re

from django.db import models

from .global_search.types import GSCourse, GSCourseSection

TTermName = str
TTermYear = int


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
    level = models.CharField(max_length=10)  # eg. "316"
    title = models.CharField(max_length=100)  # eg. "Principles of Programming Lang"

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


class InstructionEntry(CommonModel):
    days_and_times = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    meeting_dates = models.CharField(max_length=100)

    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    course_section = models.ForeignKey(
        CourseSection, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="instruction_entries")

    class Meta:
        unique_together = ("term", "course_section", "days_and_times", "meeting_dates", "room")

    def __str__(self) -> str:
        return f"Instruction Entry: {self.id}"

    def __repr__(self) -> str:
        return f"<InstructionEntry(id={self.id}, room='{self.room}', instructor_id={self.instructor.id})>"

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
            instruction_entry = InstructionEntry(
                days_and_times=days_and_times,
                room=room,
                meeting_dates=meeting_dates,
                instructor=name_to_instructors_map[instructor_name],
                course_section=course_section,
                term=term,
            )

            instruction_entries.append(instruction_entry)

        return instruction_entries
