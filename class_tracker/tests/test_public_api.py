from django.test import TestCase

from ..models import Course, CourseCareer, CourseSection, School, Subject, Term

COURSE_SECTIONS_URL = "/api/v1/course-sections/"
OTHER_ORIGIN = "https://example.com"

TQueryParams = dict[str, str | int]


class PublicApiCourseSectionTests(TestCase):
    def setUp(self) -> None:
        self.queens_college = School.objects.create(name="Queens College", globalsearch_key="QNS01")
        self.baruch_college = School.objects.create(name="Baruch College", globalsearch_key="BAR01")

        self.fall_term = Term.objects.create(name="Fall Term", year=2025, globalsearch_key="1259")
        self.spring_term = Term.objects.create(
            name="Spring Term", year=2025, globalsearch_key="1252"
        )

        self.career = CourseCareer.objects.create(name="Undergraduate", globalsearch_key="UGRD")
        self.subject = Subject.objects.create(name="Computer Science", globalsearch_key="CMSC")

        self.queens_course = self._create_course(self.queens_college, level="316", designation="")
        self.baruch_course = self._create_course(self.baruch_college, level="220W", designation="W")

        self.queens_section = self._create_section(
            self.queens_course, self.fall_term, number=43070, gs_unique_id="gs-id-1"
        )
        self.queens_query_params: TQueryParams = {
            "term_code": 1259,
            "school_code": "QNS01",
            "class_number": 43070,
        }

    def _create_course(self, school: School, level: str, designation: str) -> Course:
        return Course.objects.create(
            code="CSCI",
            level=level,
            title="Programming Languages",
            designation=designation,
            subject=self.subject,
            career=self.career,
            school=school,
        )

    def _create_section(
        self,
        course: Course,
        term: Term,
        number: int,
        gs_unique_id: str,
        section_name: str = "121-LEC Regular",
    ) -> CourseSection:
        return CourseSection.objects.create(
            gs_unique_id=gs_unique_id,
            number=number,
            section=section_name,
            topic="Some Topic",
            url="https://example.com/section",
            instruction_mode="In Person",
            course=course,
            term=term,
        )

    def test_returns_section_matching_term_school_and_class_number(self) -> None:
        response = self.client.get(COURSE_SECTIONS_URL, self.queens_query_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "number": 43070,
                    "section": "121-LEC Regular",
                    "topic": "Some Topic",
                    "instruction_mode": "In Person",
                    "course": {
                        "code": "CSCI",
                        "level": "316",
                        "title": "Programming Languages",
                        "designation": "",
                    },
                }
            ],
        )

    def test_excludes_same_class_number_at_other_school(self) -> None:
        self._create_section(
            self.baruch_course, self.fall_term, number=43070, gs_unique_id="gs-id-2"
        )
        query_params: TQueryParams = {**self.queens_query_params, "school_code": "BAR01"}

        response = self.client.get(COURSE_SECTIONS_URL, query_params)

        self.assertEqual(response.status_code, 200)
        sections = response.json()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["course"]["level"], "220W")
        self.assertEqual(sections[0]["course"]["designation"], "W")

    def test_excludes_same_class_number_in_other_term(self) -> None:
        self._create_section(
            self.queens_course,
            self.spring_term,
            number=43070,
            gs_unique_id="gs-id-2",
            section_name="131-LEC Regular",
        )

        response = self.client.get(COURSE_SECTIONS_URL, self.queens_query_params)

        self.assertEqual(response.status_code, 200)
        section_names = [section["section"] for section in response.json()]
        self.assertEqual(section_names, ["121-LEC Regular"])

    def test_matches_school_code_regardless_of_letter_case(self) -> None:
        query_params: TQueryParams = {**self.queens_query_params, "school_code": "qns01"}

        response = self.client.get(COURSE_SECTIONS_URL, query_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_returns_every_section_sharing_a_class_number_in_creation_order(self) -> None:
        # created later, but would sort first under the model's default (course, section) ordering
        self._create_section(
            self.queens_course,
            self.fall_term,
            number=43070,
            gs_unique_id="gs-id-2",
            section_name="101-LEC Regular",
        )

        response = self.client.get(COURSE_SECTIONS_URL, self.queens_query_params)

        self.assertEqual(response.status_code, 200)
        section_names = [section["section"] for section in response.json()]
        self.assertEqual(section_names, ["121-LEC Regular", "101-LEC Regular"])

    def test_returns_empty_list_when_nothing_matches(self) -> None:
        unmatched_query_params: list[TQueryParams] = [
            {"term_code": 9999, "school_code": "QNS01", "class_number": 43070},
            {"term_code": 1259, "school_code": "NOPE", "class_number": 43070},
            {"term_code": 1259, "school_code": "QNS01", "class_number": 1},
        ]
        for query_params in unmatched_query_params:
            with self.subTest(query_params=query_params):
                response = self.client.get(COURSE_SECTIONS_URL, query_params)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), [])

    def test_rejects_missing_or_malformed_params(self) -> None:
        invalid_query_params: list[TQueryParams] = [
            {},
            {"term_code": 1259, "school_code": "QNS01"},
            {"term_code": "fall", "school_code": "QNS01", "class_number": 43070},
            {"term_code": 1259, "school_code": "QNS01", "class_number": "abc"},
        ]
        for query_params in invalid_query_params:
            with self.subTest(query_params=query_params):
                response = self.client.get(COURSE_SECTIONS_URL, query_params)

                self.assertEqual(response.status_code, 422)

    def test_allows_any_origin_on_public_api(self) -> None:
        response = self.client.get(
            COURSE_SECTIONS_URL, self.queens_query_params, headers={"origin": OTHER_ORIGIN}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertNotIn("Access-Control-Allow-Credentials", response.headers)

    def test_does_not_allow_other_origins_outside_public_api(self) -> None:
        response = self.client.get("/class_tracker/get_schools/", headers={"origin": OTHER_ORIGIN})

        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
