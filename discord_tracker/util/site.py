import logging

from django.db.models import QuerySet

from discord_tracker.models import Alert, DiscordUser, TUserRoleValue, UserAlert

logger = logging.getLogger("main")


def send_alert_to_users(
    users: list[DiscordUser],
    title: str,
    md_message: str,
) -> Alert:
    alert = Alert.objects.create(
        title=title,
        md_message=md_message,
    )

    recipients = [UserAlert(alert=alert, user=user, is_read=False) for user in users]
    UserAlert.objects.bulk_create(recipients, ignore_conflicts=True)

    logger.info("Alert sent to %d users: %s", len(users), title)
    return alert


def send_alert_to_role(
    role: TUserRoleValue,
    title: str,
    md_message: str,
) -> Alert:
    users = DiscordUser.objects.filter(role=role, is_disabled=False)

    alert = Alert.objects.create(
        title=title,
        md_message=md_message,
    )

    recipients = [UserAlert(alert=alert, user=user, is_read=False) for user in users]
    UserAlert.objects.bulk_create(recipients, ignore_conflicts=True)

    user_count = len(recipients)
    logger.info(
        "Alert sent to %d users with role '%s': %s",
        user_count,
        role,
        title,
    )
    return alert


def mark_alert_as_read(alert: Alert, user: DiscordUser) -> None:
    try:
        recipient = UserAlert.objects.get(alert=alert, user=user)
        recipient.is_read = True
        recipient.save(update_fields=["is_read"])
    except UserAlert.DoesNotExist:
        logger.warning("AlertRecipient not found for alert %s and user %s", alert.id, user.id)


def get_unread_alerts_for_user(user: DiscordUser) -> list[Alert]:
    unread_recipients = UserAlert.objects.filter(user=user, is_read=False).select_related("alert")
    return [recipient.alert for recipient in unread_recipients]


def get_user_alerts(user: DiscordUser, unread_only: bool = False) -> QuerySet[UserAlert]:
    recipients = UserAlert.objects.filter(user=user)

    if unread_only:
        recipients = recipients.filter(is_read=False)

    return recipients.select_related("alert").order_by("-alert__datetime_created")
