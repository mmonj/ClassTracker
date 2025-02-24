from django.test import TestCase

from ..models import CourseCareer, CourseSection, School, Subject, Term
from . import test_parse_html_helpers as html_pars_helpers


class HtmlParser(TestCase):
    _get_soup = html_pars_helpers._get_soup  # noqa: SLF001
    _parse_main_page = html_pars_helpers._parse_main_page  # noqa: SLF001
    _refresh_semester_data = html_pars_helpers._refresh_semester_data  # noqa: SLF001
    _refresh_class_data = html_pars_helpers._refresh_class_data  # noqa: SLF001

    def test_parse_csci_fall_2024(self) -> None:
        flow_name = "flow1-2025-jan-5"

        main_page_soup = self._get_soup(flow_name, "page1")
        dept_selection_page_soup = self._get_soup(flow_name, "page2-qc-fall2024")
        class_results_page_soup = self._get_soup(flow_name, "page3-qc-fall2024-csci")
        updated_class_results_page_soup = self._get_soup(
            flow_name, "page3-qc-fall2024-csci-updated"
        )

        for class_results_soup in [
            class_results_page_soup,
            updated_class_results_page_soup,
        ]:
            self._parse_main_page(main_page_soup)

            qc_school = School.objects.get(name="Queens College")
            fall24 = Term.objects.get(year=2024, name="Fall Term")
            self._refresh_semester_data(qc_school.id, fall24.id, dept_selection_page_soup)

            School.objects.filter(globalsearch_key="QNS01").update(is_preferred=True)
            Term.objects.filter(name="Fall", year=2024).update(is_preferred=True)

            CourseCareer.objects.filter(globalsearch_key="UGRD").update(is_preferred=True)
            Subject.objects.filter(globalsearch_key="CMSC").update(is_preferred=True)

            csci_subject = Subject.objects.get(globalsearch_key="CMSC")

            self._refresh_class_data(qc_school.id, fall24.id, csci_subject.id, class_results_soup)

            # course section that is expected to have updated instruction entries
            csci_section = CourseSection.objects.prefetch_related("instruction_entries").get(
                number=56226
            )

            self.assertEqual(len(csci_section.instruction_entries.all()), 1)

    def test_parse_csci_spring_2025(self) -> None:
        flow_name = "flow2-2025-feb-23"

        main_page_soup = self._get_soup(flow_name, "page1")
        dept_selection_page_soup = self._get_soup(flow_name, "page2-qc-spring2025")
        class_results_page_soup = self._get_soup(flow_name, "page3-qc-spring2025-csci")

        for class_results_soup in [
            class_results_page_soup,
            # updated_class_results_page_soup,
        ]:
            self._parse_main_page(main_page_soup)

            qc_school = School.objects.get(name="Queens College")
            fall24 = Term.objects.get(year=2025, name="Spring Term")
            self._refresh_semester_data(qc_school.id, fall24.id, dept_selection_page_soup)

            School.objects.filter(globalsearch_key="QNS01").update(is_preferred=True)
            Term.objects.filter(name="Fall", year=2024).update(is_preferred=True)

            CourseCareer.objects.filter(globalsearch_key="UGRD").update(is_preferred=True)
            Subject.objects.filter(globalsearch_key="CMSC").update(is_preferred=True)

            csci_subject = Subject.objects.get(globalsearch_key="CMSC")

            self._refresh_class_data(qc_school.id, fall24.id, csci_subject.id, class_results_soup)

            # course section that is expected to have updated instruction entries
            csci_section = CourseSection.objects.prefetch_related("instruction_entries").get(
                number=56226
            )

            self.assertEqual(len(csci_section.instruction_entries.all()), 1)
