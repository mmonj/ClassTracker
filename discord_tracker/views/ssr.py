import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from discord_tracker.decorators import roles_required, school_required
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser, UserReferral
from discord_tracker.views import templates
from discord_tracker.views.forms import ReferralCreationForm, SchoolSelectionForm
from server.util.typedefs import AuthenticatedRequest, TPaginationData

logger = logging.getLogger("main")


@school_required
def server_listings(request: HttpRequest) -> HttpResponse:
    prefetches = ("subjects", "courses", "instructors", "schools")

    public_servers = (
        DiscordServer.objects.filter(
            privacy_level=DiscordServer.PrivacyLevel.PUBLIC, invites__approved_by__isnull=False
        )
        .distinct()
        .prefetch_related(*prefetches)
        .order_by("name")
    )

    private_servers = list(
        DiscordServer.objects.filter(
            privacy_level=DiscordServer.PrivacyLevel.PRIVATE,
            invites__approved_by__isnull=False,
        )
        .distinct()
        .prefetch_related(*prefetches)
        .order_by("name")
    )

    return templates.DiscordTrackerServerListings(
        public_servers=list(public_servers),
        private_servers=private_servers,
    ).render(request)


@require_http_methods(["GET"])
def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("discord_tracker:listings")

    return templates.DiscordTrackerLogin().render(request)


@login_required(login_url=reverse_lazy("discord_tracker:login"))
def login_success(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = DiscordUser.objects.filter(user=request.user).first()

    if discord_user is None:
        messages.warning(
            request, "Discord account not properly linked. Please contact an administrator."
        )
        return redirect("discord_tracker:listings")

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

    return redirect("discord_tracker:listings")


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


@school_required
@roles_required(required_roles=["manager"])
def unapproved_invites(request: AuthenticatedRequest) -> HttpResponse:
    unapproved_invites = (
        DiscordInvite.objects.filter(approved_by__isnull=True, rejected_by__isnull=True)
        .select_related("submitter", "discord_server")
        .order_by("-datetime_created")
    )

    return templates.DiscordTrackerUnapprovedInvites(
        unapproved_invites=list(unapproved_invites),
    ).render(request)


@school_required
@roles_required(required_roles=["regular", "manager"])
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
    return redirect("discord_tracker:listings")
