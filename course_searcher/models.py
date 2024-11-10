from django.db import models


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


class Term(CommonModel):
    globalsearch_key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    year = models.IntegerField(blank=False)
    schools = models.ManyToManyField(School, related_name="terms")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "year")

    def __str__(self) -> str:
        return self.name

    @property
    def full_term_name(self) -> str:
        return f"{self.year} {self.name}"


class Subject(CommonModel):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    globalsearch_key = models.TextField(max_length=100, unique=True)
    is_preferred = models.BooleanField(default=False)

    terms = models.ManyToManyField(Term, related_name="subjects")
    schools = models.ManyToManyField(School, related_name="subjects")

    def __str__(self) -> str:
        return f"{self.name}"


class Instructor(CommonModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CourseCareer(CommonModel):
    name = models.CharField(max_length=50)
    globalsearch_key = models.CharField(max_length=50, unique=True)
    schools = models.ManyToManyField(School, related_name="careers")

    def __str__(self) -> str:
        return f"{self.name}"


class Course(CommonModel):
    level = models.CharField(max_length=10)  # eg. "316"
    title = models.CharField(max_length=100)  # eg. "Principles of Programming Lang"
    career = models.ForeignKey(CourseCareer, on_delete=models.CASCADE, related_name="courses")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    terms = models.ManyToManyField(Term, related_name="courses")

    class Meta:
        unique_together = ("level", "school")

    def __str__(self) -> str:
        return f"{self.level} - {self.title}"


class CourseClass(CommonModel):
    class StatusChoices(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        WAITLISTED = "waitlisted", "Waitlisted"

    section = models.CharField(max_length=20)  # eg "121-LEC Regular"
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name="classes")
    room = models.CharField(max_length=50)

    days_and_times = models.CharField(max_length=100)
    meeting_dates = models.CharField(max_length=100)

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
        return f"{self.course.level} {self.section} - {self.instructor}"
