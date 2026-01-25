import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

if TYPE_CHECKING:
    from discord_tracker.models import DiscordUser

logger = logging.getLogger("main")


class DisabledUserMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated and hasattr(request.user, "discord_user"):
            discord_user: DiscordUser = request.user.discord_user  # type: ignore [attr-defined]
            if discord_user.is_disabled:
                logger.warning(
                    "Disabled user %s (id=%s) attempted access to %s",
                    discord_user.display_name,
                    discord_user.discord_id,
                    request.path,
                )
                logout(request)
                return redirect("discord_tracker:login")

        return self.get_response(request)
