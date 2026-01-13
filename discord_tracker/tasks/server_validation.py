import logging
from typing import TYPE_CHECKING, TypedDict

from django.db import transaction
from django.utils import timezone

from discord_tracker.models import DiscordInvite, DiscordServer
from discord_tracker.util.discord_api import (
    extract_invite_code_from_url,
    get_discord_invite_info,
    get_guild_creation_date,
    get_guild_icon_url,
)
from discord_tracker.util.site import send_alert_to_role

if TYPE_CHECKING:
    from discord_tracker.typedefs.discord_api import TDiscordInviteData

logger = logging.getLogger("main")


class TInvalidInvites(TypedDict):
    server_id: str
    invalid_invites: list[DiscordInvite]


def sync_discord_servers(
    server_ids: list[str] | None = None,
    limit: int = 20,
) -> list[TInvalidInvites]:
    servers_query = (
        DiscordServer.objects.enabled()
        .prefetch_related("invites")
        .filter(invites__isnull=False)
        .distinct()
    )

    if server_ids:
        servers_query = servers_query.filter(server_id__in=server_ids)

    servers_query = servers_query[:limit]

    invalid_invites_by_server: list[TInvalidInvites] = []

    for server in servers_query:
        logger.info("Syncing Discord server '%s' (ID: %s)", server.display_name, server.server_id)

        try:
            invalid_invites = _sync_single_server(server)
            if invalid_invites:
                invalid_invites_by_server.append(
                    {
                        "server_id": server.server_id,
                        "invalid_invites": invalid_invites,
                    }
                )
        except Exception as e:
            error_msg = f"Error syncing server {server.display_name}: {e}"
            logger.exception(error_msg)

    return invalid_invites_by_server


def _sync_single_server(server: DiscordServer) -> list[DiscordInvite]:
    currently_valid_invites = server.invites.filter(
        is_valid=True, datetime_approved__isnull=False
    ).order_by("-datetime_created")

    if not currently_valid_invites.exists():
        return []

    invalid_invites: list[DiscordInvite] = []
    first_valid_invite_info: TDiscordInviteData | None = None

    # check all invites for validity and fetch server data from first valid one
    for invite in currently_valid_invites:
        invite_code = extract_invite_code_from_url(invite.invite_url)
        if not invite_code:
            logger.info(
                "Invite has invalid format, marking as invalid",
                extra={"invite_url": invite.invite_url},
            )
            continue

        result = get_discord_invite_info(invite_code)
        if result.ok:
            first_valid_invite_info = result.val
        else:
            invite.is_valid = False
            invite.save(update_fields=["is_valid"])
            invalid_invites.append(invite)

    # check if all invites became invalid
    all_invites = server.invites.all()
    all_invites_invalid = (
        all_invites.exists()
        and not all_invites.filter(is_valid=True, datetime_approved__isnull=False).exists()
    )

    if all_invites_invalid:
        server.is_disabled = True
        server.save(update_fields=["is_disabled"])
        logger.warning(
            "Server disabled due to all invites being invalid",
            extra={"server_display_name": server.display_name, "server_id": server.server_id},
        )
        send_alert_to_role(
            role="manager",
            title=f"Discord Server Disabled: {server.display_name}",
            md_message=f"[Server '{server.display_name}'](/admin/discord_tracker/discordserver/{server.id}/) ({server.server_id}) has been disabled because all of its invites are no longer valid.",
        )
        return invalid_invites

    # if no valid invites found
    if first_valid_invite_info is None:
        return invalid_invites

    profile = first_valid_invite_info.get("profile")
    new_member_count = profile["member_count"] if profile else 0
    member_count_increased = new_member_count > server.member_count

    new_icon_url = get_guild_icon_url(server.server_id, first_valid_invite_info["guild"]["icon"])
    icon_changed = member_count_increased and server.icon_url != new_icon_url

    new_datetime_established = get_guild_creation_date(server.server_id)
    has_established_date = server.datetime_established is not None

    if not (member_count_increased or icon_changed or not has_established_date):
        logger.info(
            "Server skipped",
            extra={"server_display_name": server.display_name, "server_id": server.server_id},
        )
        return invalid_invites

    with transaction.atomic():
        if member_count_increased:
            server.member_count = new_member_count

        if icon_changed:
            server.icon_url = new_icon_url

        if not has_established_date:
            server.datetime_established = new_datetime_established

        server.datetime_last_synced = timezone.now()
        server.save()

    logger.info(
        "Server updated",
        extra={"server_display_name": server.display_name, "server_id": server.server_id},
    )
    return invalid_invites
