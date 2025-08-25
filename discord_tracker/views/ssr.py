from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from discord_tracker.decorators import school_required
from discord_tracker.models import DiscordServer, DiscordUser
from discord_tracker.views import templates
from discord_tracker.views.forms import SchoolSelectionForm
from server.util.typedefs import AuthenticatedRequest


@school_required
def index(request: HttpRequest) -> HttpResponse:
    public_servers = DiscordServer.objects.filter(
        privacy_level=DiscordServer.PrivacyLevel.PUBLIC
    ).order_by("name")

    # get privileged servers (only visible to trusted/manager users)
    privileged_servers = DiscordServer.objects.none()

    if request.user.is_authenticated:
        discord_user = request.user.discord_user

        if discord_user.is_trusted or discord_user.is_manager:
            privileged_servers = DiscordServer.objects.filter(
                privacy_level=DiscordServer.PrivacyLevel.PRIVILEGED
            ).order_by("name")

    return templates.DiscordTrackerIndex(
        public_servers=list(public_servers),
        privileged_servers=list(privileged_servers),
    ).render(request)


@require_http_methods(["GET"])
def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("discord_tracker:index")

    return templates.DiscordTrackerLogin().render(request)


@login_required
def login_success(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = DiscordUser.objects.filter(user=request.user).first()

    if discord_user is None:
        messages.warning(
            request, "Discord account not properly linked. Please contact an administrator."
        )
        return redirect("discord_tracker:index")

    discord_user.last_login = timezone.now()
    discord_user.save(update_fields=["last_login"])

    is_first_login = discord_user.login_count == 1

    if is_first_login:
        messages.success(
            request,
            f"Welcome, {discord_user.display_name}! Thanks for signing up via Discord.",
        )
    else:
        messages.success(
            request,
            f"Welcome back, {discord_user.display_name}! Successfully logged in via Discord.",
        )

    if discord_user.school is None:
        return redirect(reverse("discord_tracker:profile"))

    return redirect("discord_tracker:index")


@login_required
def profile(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    is_show_school_modal = discord_user.school is None

    school_form = SchoolSelectionForm(instance=discord_user)

    return templates.DiscordTrackerProfile(
        discord_user=discord_user,
        school=discord_user.school,
        school_form=school_form,
        show_school_modal=is_show_school_modal,
    ).render(request)
