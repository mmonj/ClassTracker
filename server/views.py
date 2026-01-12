from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from server import templates


def index(request: HttpRequest) -> HttpResponse:
    if (
        not request.user.is_authenticated
        or request.user.discord_user is None
        or request.user.discord_user.role_info.value != "manager"
    ):
        return redirect("discord_tracker:welcome")

    return templates.Index().render(request)
