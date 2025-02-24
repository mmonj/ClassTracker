import logging
from typing import Callable

import requests
from requests import RequestException, Response, Session
from requests.adapters import HTTPAdapter, Retry

from .types import Failure, Result, Success

logger = logging.getLogger("main")


def init_http_retrier(num_retries: int = 3, backoff_factor: float = 0.1) -> Session:
    session = requests.Session()

    retry_strategy = Retry(
        total=num_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
    )

    session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    return session


def get_response_result(
    request_callback: Callable[[], Response],
) -> Result[Response, RequestException]:
    try:
        resp = request_callback()
        return Success(value=resp)
    except RequestException as exc:
        return Failure(err=exc)
