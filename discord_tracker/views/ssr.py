from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from discord_tracker.views import templates


def index(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("discord_tracker:index")

    return templates.DiscordTrackerIndex(title="Discord Tracker").render(request)
