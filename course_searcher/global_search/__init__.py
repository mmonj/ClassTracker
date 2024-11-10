import logging
import time
from typing import Callable

from requests import RequestException, Response

logger = logging.getLogger("main")


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
