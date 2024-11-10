import logging
import time
from typing import Any, Callable, Literal, Mapping

from requests import RequestException, Response, Session

logger = logging.getLogger("main")


def get_page_resp_text(
    url: str,
    session: Session,
    method: Literal["GET", "POST"],
    payload: Mapping[str, Any] = {},
    max_retries: int = 2,
    delay_secs: float = 2.0,
    timeout: float = 10,
) -> Response:
    resp: Response
    attempts = 0
    while attempts < max_retries:
        try:
            attempts += 1
            if method == "GET":
                resp = session.get(url, data=payload, timeout=timeout)
            else:
                resp = session.post(url, data=payload, timeout=timeout)

            if not resp.ok:
                continue

            return resp

        except RequestException as e:
            logger.warning("Request failed (attempt %s/%s): {str(e)}", attempts, max_retries)

            if attempts >= max_retries:
                raise RequestException(f"Failed to fetch {url} after {max_retries} attempts") from e

            time.sleep(delay_secs)

    raise RequestException(f"Failed to fetch {url}")


def get_response(
    callback: Callable[[], Response],
    max_retries: int = 2,
    delay_secs: float = 2.0,
) -> Response:
    attempts = 0
    while attempts < max_retries:
        try:
            attempts += 1
            resp = callback()

            if not resp.ok:
                if attempts >= max_retries:
                    resp.raise_for_status()
                time.sleep(delay_secs)
                continue

            return resp

        except RequestException as _exc:
            if attempts >= max_retries:
                raise

            time.sleep(delay_secs)
            continue

    raise RequestException(f"Failed after {max_retries} attempts")
