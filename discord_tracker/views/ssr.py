from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from discord_tracker.decorators import roles_required, school_required
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser
from discord_tracker.views import templates
from discord_tracker.views.forms import SchoolSelectionForm
from server.util.typedefs import AuthenticatedRequest


@school_required
def index(request: HttpRequest) -> HttpResponse:
    prefetches = ("subjects", "courses", "instructors", "schools")

    public_servers = (
        DiscordServer.objects.filter(privacy_level=DiscordServer.PrivacyLevel.PUBLIC)
        .prefetch_related(*prefetches)
        .order_by("name")
    )

    privileged_servers = (
        DiscordServer.objects.filter(privacy_level=DiscordServer.PrivacyLevel.PRIVILEGED)
        .prefetch_related(*prefetches)
        .order_by("name")
    )

    return templates.DiscordTrackerIndex(
        public_servers=list(public_servers),
        privileged_servers=list(privileged_servers),
    ).render(request)


@require_http_methods(["GET"])
def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("discord_tracker:index")

    return templates.DiscordTrackerLogin().render(request)


@login_required(login_url=reverse_lazy("discord_tracker:login"))
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


@login_required(login_url=reverse_lazy("discord_tracker:login"))
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


@roles_required(required_roles=["manager"])
def unapproved_invites(request: AuthenticatedRequest) -> HttpResponse:
    unapproved_invites = (
        DiscordInvite.objects.filter(datetime_approved__isnull=True)
        .select_related("submitter", "discord_server")
        .order_by("-datetime_created")
    )

    return templates.DiscordTrackerUnapprovedInvites(
        unapproved_invites=list(unapproved_invites),
    ).render(request)
