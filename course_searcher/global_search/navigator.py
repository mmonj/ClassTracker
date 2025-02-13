import logging

from requests import Session

from ..models import CourseCareer, School, Subject, Term
from . import get_response_result

logger = logging.getLogger("main")

GLOBALSEARCH_URL = "https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController"
BASE_GLOBALSEARCH_URL = "https://globalsearch.cuny.edu"


def get_new_search_page(session: Session, timeout: float = 10) -> str:
    headers = _get_request_headers()
    data = {
        "new_search": "New Search",
    }

    response = session.post(GLOBALSEARCH_URL, headers=headers, data=data, timeout=timeout)

    if not response.ok:
        response.raise_for_status()

    return response.text


def get_main_page(session: Session) -> str:
    resp_result = get_response_result(lambda: session.get(GLOBALSEARCH_URL, timeout=10))
    if not resp_result.ok:
        raise resp_result.err

    return resp_result.value.text


def get_subject_selection_page(session: Session, school: School, term: Term) -> str:
    headers = _get_request_headers()
    data = _get_payload_for_subject_data(school, term)

    resp_result = get_response_result(
        lambda: session.post(
            GLOBALSEARCH_URL,
            headers=headers,
            data=data,
            timeout=10,
        )
    )

    if not resp_result.ok:
        raise resp_result.err

    return resp_result.value.text


def get_classlist_result_page(
    session: Session, course_career: CourseCareer, subject: Subject
) -> str:
    headers = _get_request_headers()
    data = _get_payload_for_class_result_page(course_career, subject)

    resp_result = get_response_result(
        lambda: session.post(
            GLOBALSEARCH_URL,
            headers=headers,
            data=data,
            timeout=10,
        )
    )

    if not resp_result.ok:
        raise resp_result.err

    return resp_result.value.text


def _get_request_headers() -> dict[str, str]:
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_GLOBALSEARCH_URL,
        "Referer": GLOBALSEARCH_URL,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


def _get_payload_for_subject_data(school: School, term: Term) -> dict[str, str]:
    return {
        "selectedInstName": f"{school.name} | ",
        "inst_selection": school.globalsearch_key,
        "selectedTermName": term.full_term_name,
        "term_value": term.globalsearch_key,
        "next_btn": "Next",
    }


def _get_payload_for_class_result_page(
    course_career: CourseCareer, subject: Subject
) -> dict[str, str]:
    return {
        "selectedSubjectName": subject.name,
        "subject_name": subject.globalsearch_key,
        "selectedCCareerName": course_career.name,
        "courseCareer": course_career.globalsearch_key,
        "selectedCAttrName": "",
        "courseAttr": "",
        "selectedCAttrVName": "",
        "courseAttValue": "",
        "selectedReqDName": "",
        "reqDesignation": "",
        "selectedSessionName": "",
        "class_session": "",
        "selectedModeInsName": "",
        "meetingStart": "LT",
        "selectedMeetingStartName": "less than",
        "meetingStartText": "",
        "AndMeetingStartText": "",
        "meetingEnd": "LE",
        "selectedMeetingEndName": "less than or equal to",
        "meetingEndText": "",
        "AndMeetingEndText": "",
        "daysOfWeek": "I",
        "selectedDaysOfWeekName": "include only these days",
        "instructor": "B",
        "selectedInstructorName": "begins with",
        "instructorName": "",
        "search_btn_search": "Search",
    }
