import logging
from typing import Iterable, cast

from bs4 import BeautifulSoup, Comment, Doctype, PageElement, ProcessingInstruction, Tag

from server.util import bulk_create_and_get

from .. import models

logger = logging.getLogger("main")


def get_terms_available(soup: BeautifulSoup) -> list[models.Term]:
    term_select_elm = soup.find("select", attrs={"name": "term_value"})
    if not term_select_elm or not isinstance(term_select_elm, Tag):
        return []

    terms: list[models.Term] = []

    for term_option in term_select_elm.find_all("option"):
        global_search_key = term_option.get("value").strip()
        full_term_name = term_option.text.strip()
        if global_search_key == "" or full_term_name == "":
            continue

        term_name, term_year = models.Term.get_term_name_and_year(full_term_name)

        if term_name is None or term_year is None:
            raise ValueError("Term_year_name match not found")

        terms.append(
            models.Term(
                name=term_name,
                year=term_year,
                globalsearch_key=global_search_key,
            )
        )

    return terms


def parse_schools(soup: BeautifulSoup) -> list[models.School]:
    institution_checkboxes = soup.find_all("input", attrs={"name": "inst_selection"})

    schools: list[models.School] = []
    for institution_checkbox in institution_checkboxes:
        school_globalsearch_key = institution_checkbox.get("value").strip()
        school_name = institution_checkbox.find_next("label")

        if school_name is None or school_globalsearch_key == "":
            continue

        school = models.School(
            name=school_name.text.strip(), globalsearch_key=school_globalsearch_key
        )
        schools.append(school)

    return schools


def create_careers_and_subjects(
    soup: BeautifulSoup, school: models.School, term: models.Term
) -> tuple[list[models.CourseCareer], list[models.Subject]]:
    # Parse course careers
    career_select = soup.select_one("#courseCareerId")
    if not career_select:
        raise ValueError("Element with selector #courseCareerId not found")

    careers_to_create = [
        models.CourseCareer(name=option.get_text(strip=True), globalsearch_key=str(option["value"]))
        for option in career_select.select("option")
        if option.get("value")  # Skips empty option
    ]

    # Bulk create careers
    careers = bulk_create_and_get(
        models.CourseCareer, careers_to_create, unique_fieldname="globalsearch_key"
    )

    # Parse department
    subject_select = soup.select_one("#subject_ld")
    if not subject_select:
        raise ValueError("Element with selector #subject_ld not found")

    subjects_to_create: list[models.Subject] = []
    for subject_option in subject_select.select("option"):
        subject_globalsearch_key = subject_option.get("value")
        if not subject_globalsearch_key:
            continue

        subjects_to_create.append(
            models.Subject(
                name=subject_option.text,
                globalsearch_key=str(subject_globalsearch_key),
            )
        )

    subjects = bulk_create_and_get(
        models.Subject, subjects_to_create, unique_fieldname="globalsearch_key"
    )

    term.subjects.add(*subjects)
    school.subjects.add(*subjects)

    term.careers.add(*careers)
    school.careers.add(*careers)

    return list(careers), list(subjects)


def _is_proper_tag_element(element: PageElement) -> bool:
    return (
        isinstance(element, Tag)
        and element.name != "br"
        and not isinstance(element, Comment | Doctype | ProcessingInstruction)
    )


def _find_next_tag_sibling(tag: Tag) -> Tag | None:
    next_sibling = tag.next_sibling

    while next_sibling is not None:
        if _is_proper_tag_element(next_sibling):
            return cast(Tag, next_sibling)
        next_sibling = next_sibling.next_sibling

    return None


def _filter_for_tag_elements(elements: Iterable[Tag | PageElement]) -> list[Tag]:
    return [cast(Tag, elm) for elm in elements if _is_proper_tag_element(elm)]
