from requests import Session

from ..models import School, Term
from . import get_page_resp_text, get_response

GLOBALSEARCH_URL = "https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp"
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
    page_src = get_response(lambda: session.get(GLOBALSEARCH_URL, timeout=10))
    return page_src.text


def get_subject_selection_page(
    session: Session, school: School, term: Term, skip_first_page: bool = False
) -> str:
    if not skip_first_page:
        get_main_page(session)

    resp = get_page_resp_text(
        GLOBALSEARCH_URL, session, "POST", payload=_get_payload_for_subject_data(school, term)
    )

    return resp.text


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
        "selectedTermName": term.name,
        "term_value": term.globalsearch_key,
        "next_btn": "Next",
    }
