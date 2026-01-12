import logging
from typing import Any

from django.core.management.base import BaseCommand

from discord_tracker.tasks.server_validation import sync_discord_servers

logger = logging.getLogger("main")


class Command(BaseCommand):
    help = "Update Discord server icon, establishment date, sync timestamp, and member count"

    def handle(self, **_options: Any) -> None:
        sync_discord_servers(limit=100)
