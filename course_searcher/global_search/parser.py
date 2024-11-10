import logging
import re

from bs4 import BeautifulSoup, Tag

from ..models import School, Term

logger = logging.getLogger("main")

TERM_YEAR_REGEX = r" *(\d+) *(.+)"


def parse_schools(soup: BeautifulSoup) -> list[School]:
    checkboxes = soup.find_all("input", attrs={"name": "inst_selection"})

    schools: list[School] = []
    for checkbox in checkboxes:
        school_id = checkbox.get("value")
        label = checkbox.find_next("label")

        if label and school_id:
            school = School(name=label.text.strip(), globalsearch_key=school_id)
            schools.append(school)

    return schools


def get_terms_available(soup: BeautifulSoup) -> list[Term]:
    select = soup.find("select", attrs={"name": "term_value"})
    if not select or not isinstance(select, Tag):
        return []

    terms: list[Term] = []
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
                Term(
                    name=term_year_name_match.group(2),
                    year=int(term_year_name_match.group(1)),
                    globalsearch_key=value,
                )
            )

    return terms
