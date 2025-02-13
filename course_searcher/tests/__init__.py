from django.db.utils import IntegrityError
from django.test import TestCase

from .. import models


class ModelTests(TestCase):
    def setUp(self) -> None:
        self.school1 = models.School.objects.create(
            name="Test University", globalsearch_key="test_uni"
        )

        self.term1 = models.Term.objects.create(
            name="Fall", year=2024, globalsearch_key="fall_2024"
        )

        self.term1.schools.add(self.school1)

        self.undergrad_course_career = models.CourseCareer.objects.create(
            name="UnderGraduate", globalsearch_key="UGRD"
        )

        self.csci_subject = models.Subject.objects.create(
            name="Computer Science",
            globalsearch_key="CMSC",
        )

        self.csci_subject.terms.add(self.term1)
        self.csci_subject.schools.add(self.school1)

        self.instructor = models.Instructor.objects.create(name="John Doe")

        self.course = models.Course.objects.create(
            code="CSCI",
            level="316",
            title="Programming Languages",
            career=self.undergrad_course_career,
            school=self.school1,
            subject=self.csci_subject,
        )

    def test_term_unique_together(self) -> None:
        with self.assertRaises(IntegrityError):
            models.Term.objects.create(
                name=self.term1.name,
                year=self.term1.year,
                globalsearch_key=self.term1.globalsearch_key,
            )

    def test_career_types(self) -> None:
        with self.assertRaises(IntegrityError):
            models.CourseCareer.objects.create(name="Undergraduate", globalsearch_key="UGRD")

    def test_subject_relationships(self) -> None:
        self.assertIn(self.csci_subject, self.school1.subjects.all())
        self.assertIn(self.csci_subject, self.term1.subjects.all())

        with self.assertRaises(IntegrityError):
            models.Subject.objects.create(
                name="Computer Science",
                globalsearch_key="CMSC",
            )

    def test_course_section_creation(self) -> None:
        course_section = models.CourseSection.objects.create(
            course=self.course,
            section="121-LEC Regular",
            status=models.CourseSection.StatusChoices.OPEN,
            instruction_mode="In Person",
            term=self.term1,
        )

        with self.assertRaises(IntegrityError):
            models.CourseSection.objects.create(
                course=self.course,
                section=course_section.section,  # duplicate section for same course
                status=models.CourseSection.StatusChoices.CLOSED,
                instruction_mode="Hybrid",
                term=course_section.term,
            )
