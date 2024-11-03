from django.db.utils import IntegrityError
from django.test import TestCase

from .. import models


class ModelTests(TestCase):
    def setUp(self) -> None:
        self.school1 = models.School.objects.create(
            name="Test University", globalsearch_key="test_uni"
        )

        self.term1 = models.Term.objects.create(
            name="Fall", year=2024, globalsearch_key="fall_2024", school=self.school1
        )

        self.undergrad_course_career = models.CourseCareer.objects.create(
            name=models.CourseCareer.CareerType.UNDERGRADUATE, school=self.school1
        )

        self.csci_subject = models.Subject.objects.create(
            name="Computer Science",
            short_name="CS",
            globalsearch_key="cs_key",
            term=self.term1,
            school=self.school1,
            career=self.undergrad_course_career,
        )

        self.instructor = models.Instructor.objects.create(first_name="John", last_name="Doe")

        self.course = models.Course.objects.create(
            level="316",
            title="Programming Languages",
            career=self.undergrad_course_career,
            school=self.school1,
        )

    def test_term_unique_together(self) -> None:
        with self.assertRaises(IntegrityError):
            models.Term.objects.create(
                name=self.term1.name,
                year=self.term1.year,
                globalsearch_key=self.term1.globalsearch_key,
                school=self.term1.school,
            )

    def test_career_types(self) -> None:
        grad_career = models.CourseCareer.objects.create(
            name=models.CourseCareer.CareerType.GRADUATE, school=self.school1
        )

        with self.assertRaises(IntegrityError):
            models.CourseCareer.objects.create(
                name=grad_career.CareerType.GRADUATE, school=grad_career.school
            )

    def test_subject_relationships(self) -> None:
        self.assertIn(self.csci_subject, self.school1.subjects.all())
        self.assertIn(self.csci_subject, self.term1.subjects.all())
        self.assertIn(self.csci_subject, self.undergrad_course_career.subjects.all())

        with self.assertRaises(IntegrityError):
            models.Subject.objects.create(
                name="Computer Science",
                short_name="CS",
                globalsearch_key="cs_key",
                term=self.term1,
                school=self.school1,
                career=self.undergrad_course_career,
            )

    def test_course_class_creation(self) -> None:
        course_class = models.CourseClass.objects.create(
            course=self.course,
            section="121-LEC Regular",
            instructor=self.instructor,
            room="Room 101",
            days_and_times="MWF 10:00-10:50",
            meeting_dates="Aug 21 - Dec 15",
            status=models.CourseClass.StatusChoices.OPEN,
            instruction_mode="In Person",
            term=self.term1,
        )

        with self.assertRaises(IntegrityError):
            models.CourseClass.objects.create(
                course=self.course,
                section=course_class.section,  # duplicate section for same course
                instructor=self.instructor,
                room="Different Room",
                days_and_times="Different Times",
                meeting_dates="Different Dates",
                status=models.CourseClass.StatusChoices.CLOSED,
                instruction_mode="Hybrid",
                term=course_class.term,
            )
