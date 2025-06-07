import logging

from requests import Session

from ..models import CourseCareer, School, Subject, Term
from . import GLOBALSEARCH_ORIGIN_URL, GLOBALSEARCH_URL

logger = logging.getLogger("main")


def get_main_page(session: Session, timeout: float = 10) -> str:
    session.headers.update(
        {"sec-fetch-site": "none"},
    )

    response = session.get(GLOBALSEARCH_URL, timeout=timeout)
    response.raise_for_status()

    return response.text


def get_main_page_anew(session: Session, timeout: float = 10) -> str:
    session.headers.update(
        {
            "cache-control": "max-age=0",
            "origin": GLOBALSEARCH_ORIGIN_URL,
            "content-type": "application/x-www-form-urlencoded",
            "sec-fetch-site": "same-origin",
            "referer": GLOBALSEARCH_URL,
        }
    )

    payload = {"new_search": "New Search"}

    response = session.get(GLOBALSEARCH_URL, data=payload, timeout=timeout)
    response.raise_for_status()

    return response.text


def get_subject_selection_page(
    session: Session, school: School, term: Term, timeout: float = 10
) -> str:
    session.headers.update(
        {
            "cache-control": "max-age=0",
            "origin": GLOBALSEARCH_ORIGIN_URL,
            "content-type": "application/x-www-form-urlencoded",
            "sec-fetch-site": "same-origin",
            "referer": GLOBALSEARCH_URL,
        }
    )

    payload = {
        "selectedInstName": f"{school.name} | ",
        "inst_selection": school.globalsearch_key,
        "selectedTermName": term.full_term_name,
        "term_value": term.globalsearch_key,
        "next_btn": "Next",
    }

    response = session.post(GLOBALSEARCH_URL, data=payload, timeout=timeout)
    response.raise_for_status()

    return response.text


def get_classlist_result_page(
    session: Session,
    course_career: CourseCareer,
    subject: Subject,
    open_classes_only: bool = False,
    timeout: float = 10,
) -> str:
    session.headers.update(
        {
            "cache-control": "max-age=0",
            "origin": GLOBALSEARCH_ORIGIN_URL,
            "content-type": "application/x-www-form-urlencoded",
            "sec-fetch-site": "same-origin",
            "referer": GLOBALSEARCH_URL,
        }
    )

    payload = {
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

    if open_classes_only:
        payload["open_class"] = "O"

    response = session.post(GLOBALSEARCH_URL, data=payload, timeout=timeout)
    response.raise_for_status()

    return response.text
