import logging
from typing import Callable

import requests
from requests import RequestException, Response, Session
from requests.adapters import HTTPAdapter, Retry

from .typedefs import Failure, Result, Success

logger = logging.getLogger("main")

GLOBALSEARCH_URL = "https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController"
GLOBALSEARCH_HOST = "globalsearch.cuny.edu"
GLOBALSEARCH_ORIGIN_URL = "https://globalsearch.cuny.edu"


def init_http_retrier(
    *, headers: dict[str, str] | None = None, num_retries: int = 3, backoff_factor: float = 0.5
) -> Session:
    session = requests.Session()

    retry_strategy = Retry(
        total=num_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
    )

    session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    if headers is not None:
        session.headers.update(headers)

    return session


def get_globalsearch_headers() -> dict[str, str]:
    return {
        "host": GLOBALSEARCH_HOST,
        "connection": "keep-alive",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
    }


def get_response_result(
    request_callback: Callable[[], Response],
) -> Result[Response, RequestException]:
    try:
        resp = request_callback()
        return Success(value=resp)
    except RequestException as exc:
        return Failure(err=exc)
