import time
from pathlib import Path

from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from server.util import bulk_create_and_get

from ..global_search.parser import (
    create_careers_and_subjects,
    get_terms_available,
    parse_gs_courses,
    parse_schools,
)
from ..models import CourseCareer, CourseSection, School, Subject, Term
from ..util import create_db_courses


class HtmlParser(TestCase):
    def setUp(self) -> None:
        self.main_page_soup: BeautifulSoup = BeautifulSoup(
            (Path(__file__).parent / "html/Page 1 - institution_term_page.html").read_text(),
            "lxml",
        )
        self.dept_selection_page_soup: BeautifulSoup = BeautifulSoup(
            (Path(__file__).parent / "html/Page 2 - criteria_selection_qc.html").read_text(),
            "lxml",
        )
        self.class_results_page_soup: BeautifulSoup = BeautifulSoup(
            (Path(__file__).parent / "html/Page 3 - class results qc-csci.html").read_text(),
            "lxml",
        )

    def test_parse_pages(self) -> None:
        qc_school, fall24 = self._parse_main_page()
        self._refresh_semester_data(qc_school.id, fall24.id)

        School.objects.filter(globalsearch_key="QNS01").update(is_preferred=True)
        Term.objects.filter(name="Fall", year=2024).update(is_preferred=True)

        CourseCareer.objects.filter(globalsearch_key="UGRD").update(is_preferred=True)
        Subject.objects.filter(globalsearch_key="CMSC").update(is_preferred=True)

        csci_subject = Subject.objects.get(globalsearch_key="CMSC")

        self._refresh_class_data(qc_school.id, fall24.id, csci_subject.id)

    def _parse_main_page(self) -> tuple[School, Term]:
        terms_parsed = get_terms_available(self.main_page_soup)
        if len(terms_parsed) == 0:
            raise ValueError("Parsed 0 terms")

        count = 0
        for term in terms_parsed:
            try:
                term.save()
                count += 1
            except IntegrityError:
                continue

        schools = sorted(parse_schools(self.main_page_soup), key=lambda school: school.name)
        schools_db = bulk_create_and_get(School, schools, unique_fieldnames=["globalsearch_key"])
        self.assertTrue(len(schools_db) > 0)

        Term.objects.all().update(is_available=False)

        terms_db = Term.objects.filter(
            globalsearch_key__in=[f.globalsearch_key for f in terms_parsed]
        )
        for term in terms_db:
            term.is_available = True
            term.save(update_fields=["is_available"])
            term.schools.add(*schools_db)

        # begin check

        for term in terms_db:
            self.assertTrue(len(term.schools.all()) > 0)

        for school in schools_db:
            self.assertTrue(len(school.terms.all()) > 0)

        # for term in terms_db:
        #     for school in term.schools.all():
        #         print(repr(school))
        #     print()

        # print()
        # for school in schools_db:
        #     for term in school.terms.all():
        #         print(repr(term))
        #     print()

        qc_school = next(f for f in schools_db if f.name == "Queens College")
        fall24 = next(
            (f for f in terms_db if f.name == "Fall Term" and f.year == 2024),  # noqa: PLR2004
        )

        return qc_school, fall24

    def _refresh_semester_data(self, school_id: int, term_id: int) -> None:
        term = Term.objects.filter(id=term_id).first()
        if term is None:
            raise ValueError([f"Term id {term_id} not found"])

        schools = (
            list(School.objects.prefetch_related("terms").all())
            if school_id == 0
            else [School.objects.prefetch_related("terms").get(id=school_id)]
        )

        for school in schools:
            subjects_page_soup = self.dept_selection_page_soup

            course_careers, subjects = create_careers_and_subjects(subjects_page_soup, school, term)

            self.assertTrue(len(school.subjects.all()) > 0)
            self.assertTrue(len(school.careers.all()) > 0)
            self.assertTrue(len(term.subjects.all()) > 0)
            self.assertTrue(len(term.careers.all()) > 0)

    def _refresh_class_data(self, school_id: int, term_id: int, subject_id: int) -> None:
        schools = (
            list(School.objects.prefetch_related("terms").all())
            if school_id == 0
            else [School.objects.prefetch_related("terms").get(id=school_id)]
        )

        term = Term.objects.get(id=term_id)

        num_csci_courses_expected = 31
        minimum_num_sections_expected = 100

        for school in schools:
            print(f"Processing school: {school!r}")

            course_careers = CourseCareer.objects.filter(terms__id=term_id, schools__id=school.id)
            for career in course_careers:
                print(repr(career))
            print()

            subjects: QuerySet[Subject]
            if subject_id == 0:
                subjects = Subject.objects.filter(terms__id=term_id, schools__id=school.id)
            else:
                subjects = Subject.objects.filter(id=subject_id)

            for subject in subjects:
                print(repr(subject))
            print()

            # session = Session()
            # get_subject_selection_page(session, school, term)

            for career in course_careers:
                #### TODO: REMOVE
                if career.globalsearch_key != "UGRD":
                    continue
                for subject in subjects:
                    #### TODO: REMOVE
                    if subject.globalsearch_key != "CMSC":
                        continue

                    # class_result_soup = get_classlist_result_page(session, career, subject)
                    class_result_soup = self.class_results_page_soup

                    gs_courses = parse_gs_courses(class_result_soup)
                    courses = create_db_courses(gs_courses, subject, career, school, term)

                    self.assertTrue(len(courses) == num_csci_courses_expected)

                    time.sleep(0.5)

        self.assertTrue(len(CourseSection.objects.all()) > minimum_num_sections_expected)
