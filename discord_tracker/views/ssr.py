import logging
from typing import TYPE_CHECKING, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from discord_tracker.decorators import require_roles, school_required
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser, UserReferral
from discord_tracker.views import templates
from discord_tracker.views.forms import ReferralCreationForm, SchoolSelectionForm
from server.util import get_pagination_data
from server.util.typedefs import AuthenticatedRequest, TPaginationData

if TYPE_CHECKING:
    from class_tracker.models import School

logger = logging.getLogger("main")


@school_required(is_api=False)
def welcome(request: HttpRequest) -> HttpResponse:
    prefetches = ("subjects", "courses", "instructors", "schools")
    page_size = 10

    queryset_school_args = {}
    discord_user: DiscordUser | None = None

    if (
        request.user.is_authenticated
        and (discord_user := DiscordUser.objects.filter(user=request.user).first()) is not None
    ):
        user_school = cast("School", discord_user.school)
        if user_school is not None:
            queryset_school_args["schools"] = user_school

    base_queryset = (
        DiscordServer.objects.filter(invites__approved_by__isnull=False, **queryset_school_args)
        .distinct()
        .prefetch_related(*prefetches)
    )

    pending_invites_count = 0
    if discord_user is not None and discord_user.is_manager:
        pending_invites_count = DiscordInvite.objects.filter(
            approved_by__isnull=True, rejected_by__isnull=True
        ).count()

    # recent servers
    required_servers = list(base_queryset.filter(is_required_for_trust=True).order_by("-id"))

    public_servers = list(
        base_queryset.filter(
            privacy_level=DiscordServer.PrivacyLevel.PUBLIC, is_required_for_trust=False
        ).order_by("-id")[:page_size]
    )

    private_servers = list(
        base_queryset.filter(
            privacy_level=DiscordServer.PrivacyLevel.PRIVATE, is_required_for_trust=False
        ).order_by("-id")[:page_size]
    )

    servers = [*required_servers, *public_servers, *private_servers]

    return templates.DiscordTrackerWelcome(
        servers=servers,
        pending_invites_count=pending_invites_count,
    ).render(request)


@school_required(is_api=False)
@require_roles(required_roles=None, is_api=False)
def explore_all_listings(request: HttpRequest) -> HttpResponse:
    prefetches = ("subjects", "courses", "instructors", "schools")

    subject_id = request.GET.get("subject_id")
    course_id = request.GET.get("course_id")
    page_number = request.GET.get("page")
    page = int(page_number) if page_number else 1
    page_size = 15

    queryset_school_args = {}
    discord_user: DiscordUser | None = None

    if (
        request.user.is_authenticated
        and (discord_user := DiscordUser.objects.filter(user=request.user).first()) is not None
    ):
        user_school = cast("School", discord_user.school)
        if user_school is not None:
            queryset_school_args["schools"] = user_school

    base_queryset = (
        DiscordServer.objects.filter(invites__approved_by__isnull=False, **queryset_school_args)
        .distinct()
        .prefetch_related(*prefetches)
    )

    pending_invites_count = 0
    if discord_user is not None and discord_user.is_manager:
        pending_invites_count = DiscordInvite.objects.filter(
            approved_by__isnull=True, rejected_by__isnull=True
        ).count()

    search_queryset = base_queryset.order_by(
        "-is_required_for_trust",
        "courses__code",
        "courses__level",
        "name",
    )

    if subject_id:
        search_queryset = search_queryset.filter(subjects__id=subject_id)

    if course_id:
        search_queryset = search_queryset.filter(courses__id=course_id)

    page_obj, pagination_data = get_pagination_data(search_queryset, page=page, page_size=page_size)

    is_search_active = bool(subject_id or course_id)

    return templates.DiscordTrackerExploreAll(
        servers=list(page_obj.object_list),
        pagination=pagination_data,
        subject_id=int(subject_id) if subject_id else None,
        course_id=int(course_id) if course_id else None,
        is_search_active=is_search_active,
        pending_invites_count=pending_invites_count,
    ).render(request)


@require_http_methods(["GET"])
def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("discord_tracker:welcome")

    return templates.DiscordTrackerLogin().render(request)


@login_required(login_url=reverse_lazy("discord_tracker:login"))
def login_success(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = DiscordUser.objects.filter(user=request.user).first()

    if discord_user is None:
        messages.warning(
            request, "Discord account not properly linked. Please contact an administrator."
        )
        return redirect("discord_tracker:welcome")

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

    return redirect("discord_tracker:welcome")


@login_required(login_url=reverse_lazy("discord_tracker:login"))
@require_http_methods(["GET"])
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


@school_required(is_api=False)
@require_roles(required_roles=["manager"], is_api=False)
def unapproved_invites(request: AuthenticatedRequest) -> HttpResponse:
    unapproved_invites = (
        DiscordInvite.objects.filter(approved_by__isnull=True, rejected_by__isnull=True)
        .select_related("submitter", "discord_server")
        .order_by("-datetime_created")
    )

    return templates.DiscordTrackerUnapprovedInvites(
        unapproved_invites=list(unapproved_invites),
    ).render(request)


@school_required(is_api=False)
@require_roles(required_roles=None, is_api=False)
def referral_management(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    if request.method == "POST":
        form = ReferralCreationForm(request.POST, discord_user=discord_user)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.created_by = discord_user
            referral.save()

            messages.success(
                request,
                "Referral created successfully!",
            )
            return redirect("discord_tracker:referral_management")
    else:
        form = ReferralCreationForm(discord_user=discord_user)

    # get user's previously created referrals
    referrals_queryset = (
        UserReferral.objects.filter(created_by=discord_user)
        .prefetch_related("redemptions__redeemed_by")
        .order_by("-datetime_created")
    )

    page_size = 20
    paginator = Paginator(referrals_queryset, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    pagination_data = TPaginationData(
        current_page=page_obj.number,
        total_pages=paginator.num_pages,
        has_previous=page_obj.has_previous(),
        has_next=page_obj.has_next(),
        previous_page_number=page_obj.previous_page_number() if page_obj.has_previous() else 0,
        next_page_number=page_obj.next_page_number() if page_obj.has_next() else 0,
    )

    return templates.DiscordTrackerReferralManagement(
        referral_form=form,
        referrals=list(page_obj.object_list),
        pagination=pagination_data,
    ).render(request)


@require_http_methods(["GET"])
def referral_redeem(request: HttpRequest, referral_code: str) -> HttpResponse:
    existing_referral = UserReferral.objects.filter(code=referral_code).first()
    if existing_referral is None:
        messages.error(request, "Invalid referral code.")
        return redirect("discord_tracker:login")

    if not existing_referral.is_valid():
        messages.error(request, "Invalid referral code.")
        return redirect("discord_tracker:login")

    if not request.user.is_authenticated:
        request.session["referral_code"] = referral_code
        messages.info(request, "You may now log in via Discord")
        return redirect("discord_tracker:login")

    messages.error(request, "You are already logged in")
    return redirect("discord_tracker:welcome")
