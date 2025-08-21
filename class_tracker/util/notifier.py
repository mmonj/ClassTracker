import logging
import os
from typing import Any

from server.util import init_http_retrier

from ..models import Recipient

logger = logging.getLogger("main")

DEVICE_ID = os.environ["JOINAPP_DEVICE_ID"]
API_KEY = os.environ["JOINAPP_API_KEY"]

SEND_URL = os.environ["JOINAPP_SEND_URL"]
LIST_URL = os.environ["JOINAPP_LIST_URL"]


def notify_recipient(recipient: Recipient, message: str) -> None:
    if not recipient.is_contact_by_phone:
        _notify_myself(title="Open Course Sections Alert", message=message)
        return

    first_phone = recipient.phone_numbers.filter(is_enabled=True).first()

    if first_phone is None:
        logger.warning("No enabled phone numbers found for recipient %s", recipient.name)
        return

    try:
        _send_join_sms(first_phone.number, message)
        logger.info("SMS sent successfully to %s (%s)", recipient.name, first_phone.number)
    except Exception:
        logger.exception("Failed to send SMS to %s (%s)", recipient.name, first_phone.number)


def _notify_myself(title: str, message: str, url: str = "") -> None:
    if url == "":
        _send_join_notification_text(
            title="Open Course Section(s)", text=message, device_id=DEVICE_ID
        )
    else:
        _send_join_notification_url(url=url, title=title, text=message, device_id=DEVICE_ID)


def _send_join_sms(sms_number: str, sms_text: str) -> None:
    params = {
        "apikey": API_KEY,
        "smsnumber": sms_number,
        "smstext": sms_text,
        "deviceId": DEVICE_ID,
    }

    session = init_http_retrier(num_retries=3)
    session.get(SEND_URL, params=params)


def _send_join_notification_text(
    text: str,
    title: str | None = None,
    device_id: str | None = None,
    device_ids: list[str] | None = None,
    device_names: list[str] | None = None,
    icon: Any = None,
    smallicon: Any = None,
    vibration: Any = None,
) -> bool:
    if device_id is None and device_ids is None and device_names is None:
        return False
    params = {
        "apikey": API_KEY,
        "text": text,
        "title": title,
        "icon": icon,
        "smallicon": smallicon,
        "vibration": vibration,
        "deviceId": device_id,
        "deviceIds": device_ids,
        "deviceNames": device_names,
    }

    session = init_http_retrier(num_retries=3)
    session.get(SEND_URL, params=params, timeout=10)
    return True


def _send_join_notification_url(
    url: str,
    text: str | None = None,
    title: str | None = None,
    device_id: str | None = None,
    device_ids: list[str] | None = None,
    device_names: list[str] | None = None,
) -> bool:
    if device_id is None and device_ids is None and device_names is None:
        return False
    params = {
        "apikey": API_KEY,
        "url": url,
        "title": title,
        "text": text,
        "deviceId": device_id,
        "deviceIds": device_ids,
        "deviceNames": device_names,
    }

    session = init_http_retrier(num_retries=3)
    session.get(SEND_URL, params=params, timeout=10)
    return True
