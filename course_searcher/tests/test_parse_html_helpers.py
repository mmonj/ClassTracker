from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from server.util import bulk_create_and_get

from ..global_search.parser import (
    create_careers_and_subjects,
    get_terms_available,
    parse_gs_courses,
    parse_schools,
)
from ..models import CourseCareer, CourseSection, School, Subject, Term
from ..util import create_db_courses

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .test_parse_html import HtmlParser


def _get_soup(_self: HtmlParser, html_flow: str, doc_name: str) -> BeautifulSoup:
    file_path = Path(__file__).parent / f"html/{html_flow}/{doc_name}.html"
    return BeautifulSoup(file_path.read_text(), "html.parser")


def _parse_main_page(self: HtmlParser, main_page_soup: BeautifulSoup) -> None:
    terms_parsed = get_terms_available(main_page_soup)
    if len(terms_parsed) == 0:
        raise ValueError("Parsed 0 terms")

    prev_terms_count = len(Term.objects.all())
    terms_db = bulk_create_and_get(Term, terms_parsed, fields=["globalsearch_key"])
    new_terms_count = len(Term.objects.all()) - prev_terms_count

    schools = sorted(parse_schools(main_page_soup), key=lambda school: school.name)
    schools_db = bulk_create_and_get(School, schools, fields=["globalsearch_key"])
    self.assertGreater(len(schools_db), 0)

    Term.objects.all().update(is_available=False)
    for term in terms_db:
        term.is_available = True
        term.save(update_fields=["is_available"])
        term.schools.add(*schools_db)

    # begin check

    for term in terms_db:
        self.assertGreater(len(term.schools.all()), 0)

    for school in schools_db:
        self.assertGreater(len(school.terms.all()), 0)

    # for term in terms_db:
    #     for school in term.schools.all():
    #         print(repr(school))
    #     print()

    # print()
    # for school in schools_db:
    #     for term in school.terms.all():
    #         print(repr(term))
    #     print()

    # TODO: remove
    print(f"{new_terms_count} new terms created")


def _refresh_semester_data(
    self: HtmlParser, school_id: int, term_id: int, dept_selection_page_soup: BeautifulSoup
) -> None:
    term = Term.objects.filter(id=term_id).first()
    if term is None:
        raise ValueError([f"Term id {term_id} not found"])

    schools = (
        list(School.objects.prefetch_related("terms").all())
        if school_id == 0
        else [School.objects.prefetch_related("terms").get(id=school_id)]
    )

    for school in schools:
        subjects_page_soup = dept_selection_page_soup

        course_careers, subjects = create_careers_and_subjects(subjects_page_soup, school, term)

        self.assertGreater(len(school.subjects.all()), 0)
        self.assertGreater(len(school.careers.all()), 0)
        self.assertGreater(len(term.subjects.all()), 0)
        self.assertGreater(len(term.careers.all()), 0)


def _refresh_class_data(
    self: HtmlParser,
    school_id: int,
    term_id: int,
    subject_id: int,
    class_results_soup: BeautifulSoup,
) -> None:
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
                class_result_soup = class_results_soup

                gs_courses = parse_gs_courses(class_result_soup)
                courses = create_db_courses(gs_courses, subject, career, school, term)

                self.assertEqual(len(courses), num_csci_courses_expected)

                time.sleep(0.5)

    self.assertGreater(len(CourseSection.objects.all()), minimum_num_sections_expected)
