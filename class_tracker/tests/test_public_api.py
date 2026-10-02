from django.test import TestCase

from ..models import Course, CourseCareer, CourseSection, School, Subject, Term

COURSE_SECTIONS_URL = "/api/v1/course-sections/"
VARIABLE_TOPIC_SECTIONS_URL = "/api/v1/course-sections/variable-topic/"
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


class PublicApiVariableTopicSectionTests(TestCase):
    def setUp(self) -> None:
        self.queens_college = School.objects.create(name="Queens College", globalsearch_key="QNS01")
        self.baruch_college = School.objects.create(name="Baruch College", globalsearch_key="BAR01")

        self.fall_term = Term.objects.create(name="Fall Term", year=2025, globalsearch_key="1259")
        self.spring_term = Term.objects.create(
            name="Spring Term", year=2025, globalsearch_key="1252"
        )

        self.career = CourseCareer.objects.create(name="Undergraduate", globalsearch_key="UGRD")
        self.subject = Subject.objects.create(name="Computer Science", globalsearch_key="CMSC")

        self.special_topics_course = self._create_course(
            self.queens_college, code="CSCI", level="381", title="VT: Special Topics in Comp Sci"
        )
        self.fixed_topic_course = self._create_course(
            self.queens_college, code="CSCI", level="316", title="Programming Languages"
        )
        self.queens_query_params: TQueryParams = {"term_code": 1259, "school_code": "QNS01"}

    def _create_course(
        self, school: School, code: str, level: str, title: str, designation: str = ""
    ) -> Course:
        return Course.objects.create(
            code=code,
            level=level,
            title=title,
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
        topic: str,
        section_name: str = "121-LEC Regular",
    ) -> CourseSection:
        return CourseSection.objects.create(
            gs_unique_id=f"gs-id-{number}",
            number=number,
            section=section_name,
            topic=topic,
            url="https://example.com/section",
            instruction_mode="In Person",
            course=course,
            term=term,
        )

    def _get_topics(self, query_params: TQueryParams) -> list[str]:
        response = self.client.get(VARIABLE_TOPIC_SECTIONS_URL, query_params)

        self.assertEqual(response.status_code, 200)
        return [section["topic"] for section in response.json()]

    def test_returns_only_sections_whose_topic_differs_from_course_title(self) -> None:
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        self._create_section(
            self.fixed_topic_course, self.fall_term, number=43071, topic="Programming Languages"
        )

        response = self.client.get(VARIABLE_TOPIC_SECTIONS_URL, self.queens_query_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "number": 43070,
                    "section": "121-LEC Regular",
                    "topic": "Cryptography",
                    "instruction_mode": "In Person",
                    "course": {
                        "code": "CSCI",
                        "level": "381",
                        "title": "VT: Special Topics in Comp Sci",
                        "designation": "",
                    },
                }
            ],
        )

    def test_ignores_letter_case_when_comparing_topic_to_course_title(self) -> None:
        self._create_section(
            self.fixed_topic_course, self.fall_term, number=43071, topic="PROGRAMMING LANGUAGES"
        )

        self.assertEqual(self._get_topics(self.queens_query_params), [])

    def test_narrows_to_course_code_regardless_of_letter_case(self) -> None:
        math_studies_course = self._create_course(
            self.queens_college, code="MATH", level="3903", title="Studies in Mathematics"
        )
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        self._create_section(
            math_studies_course, self.fall_term, number=43071, topic="Numerical Analysis I"
        )

        for course_code in ("MATH", "math"):
            with self.subTest(course_code=course_code):
                query_params: TQueryParams = {
                    **self.queens_query_params,
                    "course_code": course_code,
                }

                self.assertEqual(self._get_topics(query_params), ["Numerical Analysis I"])

    def test_narrows_to_course_level_including_its_designation_suffix(self) -> None:
        writing_intensive_course = self._create_course(
            self.queens_college,
            code="CSCI",
            level="381W",
            title="VT: Special Topics in Comp Sci",
            designation="W",
        )
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        self._create_section(
            writing_intensive_course, self.fall_term, number=43071, topic="Computing and Society"
        )

        expected_topics_by_course_level = {
            "381": ["Cryptography"],
            "381W": ["Computing and Society"],
            "381w": ["Computing and Society"],
        }
        for course_level, expected_topics in expected_topics_by_course_level.items():
            with self.subTest(course_level=course_level):
                query_params: TQueryParams = {
                    **self.queens_query_params,
                    "course_code": "CSCI",
                    "course_level": course_level,
                }

                self.assertEqual(self._get_topics(query_params), expected_topics)

    def test_rejects_course_level_without_course_code(self) -> None:
        query_params: TQueryParams = {**self.queens_query_params, "course_level": "381"}

        response = self.client.get(VARIABLE_TOPIC_SECTIONS_URL, query_params)

        self.assertEqual(response.status_code, 422)
        self.assertIn("course_code", response.json()["detail"])

    def test_orders_by_course_code_then_level_then_section(self) -> None:
        math_studies_course = self._create_course(
            self.queens_college, code="MATH", level="3903", title="Studies in Mathematics"
        )
        graduate_topics_course = self._create_course(
            self.queens_college, code="CSCI", level="780", title="Special Topics in Computer Sci"
        )
        # created in the reverse of the expected order
        self._create_section(
            math_studies_course, self.fall_term, number=43070, topic="Numerical Analysis I"
        )
        self._create_section(
            graduate_topics_course, self.fall_term, number=43071, topic="SCS: Cloud Computing"
        )
        self._create_section(
            self.special_topics_course,
            self.fall_term,
            number=43072,
            topic="Quantum Computing",
            section_name="131-LEC Regular",
        )
        self._create_section(
            self.special_topics_course,
            self.fall_term,
            number=43073,
            topic="Cryptography",
            section_name="121-LEC Regular",
        )

        self.assertEqual(
            self._get_topics(self.queens_query_params),
            ["Cryptography", "Quantum Computing", "SCS: Cloud Computing", "Numerical Analysis I"],
        )

    def test_excludes_variable_topic_sections_of_other_terms_and_schools(self) -> None:
        baruch_topics_course = self._create_course(
            self.baruch_college, code="CSCI", level="381", title="VT: Special Topics in Comp Sci"
        )
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        self._create_section(
            self.special_topics_course, self.spring_term, number=43071, topic="Computer Vision"
        )
        self._create_section(
            baruch_topics_course, self.fall_term, number=43072, topic="Internet Security"
        )

        self.assertEqual(self._get_topics(self.queens_query_params), ["Cryptography"])
        self.assertEqual(
            self._get_topics({"term_code": 1259, "school_code": "bar01"}), ["Internet Security"]
        )

    def test_returns_empty_list_when_nothing_matches(self) -> None:
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        unmatched_query_params: list[TQueryParams] = [
            {"term_code": 9999, "school_code": "QNS01"},
            {"term_code": 1259, "school_code": "NOPE"},
            {"term_code": 1259, "school_code": "QNS01", "course_code": "NOPE"},
            {"term_code": 1259, "school_code": "QNS01", "course_code": "CSCI", "course_level": "1"},
        ]
        for query_params in unmatched_query_params:
            with self.subTest(query_params=query_params):
                self.assertEqual(self._get_topics(query_params), [])

    def test_rejects_missing_or_malformed_params(self) -> None:
        invalid_query_params: list[TQueryParams] = [
            {},
            {"term_code": 1259},
            {"school_code": "QNS01"},
            {"term_code": "fall", "school_code": "QNS01"},
        ]
        for query_params in invalid_query_params:
            with self.subTest(query_params=query_params):
                response = self.client.get(VARIABLE_TOPIC_SECTIONS_URL, query_params)

                self.assertEqual(response.status_code, 422)

    def test_treats_empty_course_code_and_course_level_as_omitted(self) -> None:
        self._create_section(
            self.special_topics_course, self.fall_term, number=43070, topic="Cryptography"
        )
        query_params: TQueryParams = {
            **self.queens_query_params,
            "course_code": "",
            "course_level": "",
        }

        self.assertEqual(self._get_topics(query_params), ["Cryptography"])
