"""Utility functions for site-wide operations and alerts"""

import logging
from typing import TYPE_CHECKING

from discord_tracker.models import AlertRecipient, TUserRoleValue

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from discord_tracker.models import Alert, DiscordUser

logger = logging.getLogger("main")


def send_alert_to_users(
    users: list["DiscordUser"],
    title: str,
    message: str,
) -> "Alert":
    from discord_tracker.models import Alert, AlertRecipient

    alert = Alert.objects.create(
        title=title,
        message=message,
    )

    recipients = [AlertRecipient(alert=alert, user=user, is_read=False) for user in users]
    AlertRecipient.objects.bulk_create(recipients, ignore_conflicts=True)

    logger.info(f"Alert sent to {len(users)} users: {title}")
    return alert


def send_alert_to_role(
    role: TUserRoleValue,
    title: str,
    message: str,
) -> Alert:
    # Get all users with the specified role
    users = DiscordUser.objects.filter(role=role, is_disabled=False)

    alert = Alert.objects.create(
        title=title,
        message=message,
    )

    recipients = [AlertRecipient(alert=alert, user=user, is_read=False) for user in users]
    AlertRecipient.objects.bulk_create(recipients, ignore_conflicts=True)

    user_count = len(recipients)
    logger.info(f"Alert sent to {user_count} users with role '{role}': {title}")
    return alert


def mark_alert_as_read(alert: Alert, user: DiscordUser) -> bool:
    try:
        recipient = AlertRecipient.objects.get(alert=alert, user=user)
        recipient.is_read = True
        recipient.save(update_fields=["is_read"])
        return True
    except AlertRecipient.DoesNotExist:
        logger.warning(f"AlertRecipient not found for alert {alert.id} and user {user.id}")
        return False


def get_unread_alerts_for_user(user: DiscordUser) -> list[Alert]:
    """Get all unread alerts for a specific user"""

    unread_recipients = AlertRecipient.objects.filter(user=user, is_read=False).select_related(
        "alert"
    )
    return [recipient.alert for recipient in unread_recipients]


def get_user_alerts(user: DiscordUser, unread_only: bool = False) -> QuerySet[AlertRecipient]:
    recipients = AlertRecipient.objects.filter(user=user)

    if unread_only:
        recipients = recipients.filter(is_read=False)

    return recipients.select_related("alert").order_by("-alert__datetime_created")
