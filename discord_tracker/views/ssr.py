from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from discord_tracker.models import DiscordUser
from discord_tracker.views import templates
from server.util.typedefs import AuthenticatedRequest


def index(request: HttpRequest) -> HttpResponse:
    return templates.DiscordTrackerIndex().render(request)


@require_http_methods(["GET"])
def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("discord_tracker:index")

    # Get the Discord OAuth login URL using allauth
    discord_login_url = reverse("discord_login")

    return templates.DiscordTrackerLogin(
        title="Discord Login", redirect_url=discord_login_url
    ).render(request)


@login_required
def login_success(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = DiscordUser.objects.filter(user=request.user).first()

    if discord_user is None:
        messages.warning(
            request, "Discord account not properly linked. Please contact an administrator."
        )
    else:
        discord_user.last_login = timezone.now()
        discord_user.save(update_fields=["last_login"])

        messages.success(
            request,
            f"Welcome back, {discord_user.display_name}! Successfully logged in via Discord.",
        )
    return redirect("discord_tracker:index")
