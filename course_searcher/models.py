import re

from django.db import models

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
    # custom shortname, not associated with globalsearch_key
    short_name = models.CharField(max_length=100, blank=True, default="")  # eg CSCI (comp sci)
    globalsearch_key = models.TextField(max_length=100, unique=True)  # eg. CMSC (comp sci)
    is_preferred = models.BooleanField(default=False)

    terms = models.ManyToManyField(Term, related_name="subjects")
    schools = models.ManyToManyField(School, related_name="subjects")

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}', short_name='{self.short_name}', globalsearch_key='{self.globalsearch_key}')>"


class Course(CommonModel):
    level = models.CharField(max_length=10)  # eg. "316"
    title = models.CharField(max_length=100)  # eg. "Principles of Programming Lang"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    career = models.ForeignKey(CourseCareer, on_delete=models.CASCADE, related_name="courses")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    terms = models.ManyToManyField(Term, related_name="courses")

    class Meta:
        unique_together = ("level", "school")

    def __str__(self) -> str:
        return f"{self.level} - {self.title}"

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, level='{self.level}', title='{self.title}')>"


class CourseClass(CommonModel):
    class StatusChoices(models.TextChoices):
        OPEN = ("open", "Open")
        CLOSED = ("closed", "Closed")
        WAITLISTED = ("waitlisted", "Waitlisted")

    url = models.CharField(max_length=1000, default="")
    section = models.CharField(max_length=20)  # eg "121-LEC Regular"

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN
    )
    instruction_mode = models.CharField(max_length=50)  # eg. in person, hybrid

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="classes")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="classes")

    class Meta:
        verbose_name_plural = "Course Classes"
        unique_together = ("course", "section", "term")
        ordering = ("course", "section")

    def __str__(self) -> str:
        instruction_entries = self.instruction_entries.all()
        if len(instruction_entries) == 0:
            return f"{self.course.level} {self.section} - {instruction_entries[0]}"
        return f"{self.course.level} {self.section} - {len(instruction_entries)} instructors"

    def __repr__(self) -> str:
        return f"<CourseClass(id={self.id}, section='{self.section}', status='{self.status}', instruction mode='{self.instruction_mode}')>"


class Instructor(CommonModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Instructor(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"


class InstructionEntry(CommonModel):
    days_and_times = models.CharField(max_length=100)
    meeting_dates = models.CharField(max_length=100)
    room = models.CharField(max_length=50)

    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    course_class = models.ForeignKey(
        CourseClass, on_delete=models.CASCADE, related_name="instruction_entries"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="instruction_entries")

    def __str__(self) -> str:
        return f"Instruction Entry: {self.id}"

    def __repr__(self) -> str:
        return f"<InstructionEntry(id={self.id}, room='{self.room}', instructor_id={self.instructor.id})>"
