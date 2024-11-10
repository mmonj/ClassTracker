import logging
import re

from bs4 import BeautifulSoup, Tag

from .. import models

logger = logging.getLogger("main")

TERM_YEAR_REGEX = r" *(\d+) *(.+)"


def parse_schools(soup: BeautifulSoup) -> list[models.School]:
    checkboxes = soup.find_all("input", attrs={"name": "inst_selection"})

    schools: list[models.School] = []
    for checkbox in checkboxes:
        school_id = checkbox.get("value")
        label = checkbox.find_next("label")

        if label and school_id:
            school = models.School(name=label.text.strip(), globalsearch_key=school_id)
            schools.append(school)

    return schools


def get_terms_available(soup: BeautifulSoup) -> list[models.Term]:
    select = soup.find("select", attrs={"name": "term_value"})
    if not select or not isinstance(select, Tag):
        return []

    terms: list[models.Term] = []
    for option in select.find_all("option"):
        value = option.get("value")
        full_term_name = option.text.strip()
        if value == "" or full_term_name == "":
            continue

        term_year_name_match = re.match(TERM_YEAR_REGEX, full_term_name)

        if term_year_name_match is None:
            raise ValueError("Term_year_name match not found")

        if value:
            terms.append(
                models.Term(
                    name=term_year_name_match.group(2),
                    year=int(term_year_name_match.group(1)),
                    globalsearch_key=value,
                )
            )

    return terms


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
    models.CourseCareer.objects.bulk_create(
        careers_to_create,
        ignore_conflicts=True,
    )

    careers = models.CourseCareer.objects.filter(name__in=[f.name for f in careers_to_create])

    # Add M2M relationship to school
    for career in careers:
        career.schools.add(school)

    # Parse subjects
    subject_select = soup.select_one("#subject_ld")
    if not subject_select:
        raise ValueError("Element with selector #subject_ld not found")

    subjects_to_create: list[models.Subject] = []
    for option in subject_select.select("option"):
        value = option.get("value")
        if not value:
            continue

        subjects_to_create.append(
            models.Subject(
                name=option.text,
                globalsearch_key=str(value),
                short_name=str(value),
            )
        )

    models.Subject.objects.bulk_create(subjects_to_create, ignore_conflicts=True)
    subjects = models.Subject.objects.filter(
        globalsearch_key__in=[f.globalsearch_key for f in subjects_to_create]
    )

    term.subjects.add(*subjects)
    school.subjects.add(*subjects)

    return list(careers), list(subjects)
