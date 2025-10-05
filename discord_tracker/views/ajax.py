import logging
from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from class_tracker.models import Course, Instructor, School, Subject
from discord_tracker.decorators import require_roles
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser, InviteUsage
from discord_tracker.views import interfaces_response
from discord_tracker.views.forms import SchoolSelectionForm
from server.util import error_json_response
from server.util.typedefs import AuthenticatedRequest

from ..util.discord_api import (
    extract_invite_code_from_url,
    get_discord_invite_info,
    get_guild_creation_date,
    get_guild_icon_url,
)

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger("main")


@login_required
@require_http_methods(["POST"])
def select_school(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    form = SchoolSelectionForm(request.POST, instance=discord_user)

    if form.is_valid():
        form.save()
        messages.success(request, "School selected successfully!")
        return interfaces_response.SchoolSelectionResponse(
            success=True, message="School selected successfully!"
        ).render(request)

    error_messages = [
        f"{field}: {error}" for field, errors in form.errors.items() for error in errors
    ]

    return interfaces_response.SchoolSelectionResponse(
        success=False,
        message="; ".join(error_messages) if error_messages else "Please correct the form errors.",
    ).render(request)


@require_http_methods(["GET"])
def server_invites(request: AuthenticatedRequest, server_id: int) -> HttpResponse:
    server = get_object_or_404(DiscordServer, id=server_id)
    invites = server.invites.filter(
        is_valid=True,
        datetime_approved__isnull=False,
    ).order_by("-datetime_created")

    # anyone can view public invites
    if server.privacy_level_info.value == "public":
        return interfaces_response.ServerInvitesResponse(
            invites=list(invites),
        ).render(request)

    if not request.user.is_authenticated:
        return error_json_response(["You must log in to view server invites."], status=401)

    return interfaces_response.ServerInvitesResponse(
        invites=list(invites),
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["POST"])
def validate_discord_invite(request: AuthenticatedRequest) -> HttpResponse:
    """Validate Discord invite and return server info (including existing DB data if server exists)"""
    discord_user: DiscordUser = request.user.discord_user  # type: ignore [attr-defined, unused-ignore]

    invite_url = request.POST.get("invite_url", "").strip()

    if not invite_url:
        return error_json_response(["Invite URL is required"], status=400)

    invite_code = extract_invite_code_from_url(invite_url)
    if invite_code is None:
        return error_json_response(["Invalid Discord invite URL provided"], status=400)

    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return error_json_response(
            [f"Failed to verify Discord server: {invite_result.err}"], status=400
        )

    invite_info = invite_result.val

    # expires_at=null indicates invite is permanent
    if invite_info["expires_at"] is not None:
        return error_json_response(
            [
                "Only permanent Discord invites are allowed. Please submit a non-expiring invite URL."
            ],
            status=400,
        )

    guild_id = invite_info["guild"]["id"]
    guild_name = invite_info["guild"]["name"]
    guild_icon_url = get_guild_icon_url(guild_id, invite_info["guild"]["icon"])

    # check if server already exists in database
    existing_server = DiscordServer.objects.filter(server_id=guild_id).first()

    # get available schools
    available_schools: list[School] = []
    if not discord_user.is_manager and discord_user.school is None:
        return error_json_response(["User is not a manager and has no school assigned"], status=400)

    if not discord_user.is_manager and discord_user.school is not None:
        available_schools = [discord_user.school]
    elif discord_user.is_manager:
        available_schools = list(School.objects.filter(subjects__isnull=False).distinct())

    return interfaces_response.ValidateDiscordInviteResponse(
        guild_info={
            "id": guild_id,
            "name": guild_name,
            "icon_url": guild_icon_url,
        },
        existing_server_info=existing_server,
        available_schools=available_schools,
        is_new_server=existing_server is None,
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["POST"])
def submit_invite(request: AuthenticatedRequest) -> HttpResponse:  # noqa: PLR0911, PLR0912, PLR0915
    discord_user: DiscordUser = request.user.discord_user  # type: ignore [attr-defined, unused-ignore]

    invite_url = request.POST.get("invite_url", "").strip()
    notes = request.POST.get("notes", "").strip()
    guild_name = request.POST.get("guild_name", "").strip()
    guild_id = request.POST.get("guild_id", "").strip()
    school_id = request.POST.get("school_id")
    subject_id = request.POST.get("subject_id")
    course_id = request.POST.get("course_id")
    instructor_ids = request.POST.getlist("instructor_ids")  # can be multiple instructors
    privacy_level = request.POST.get("privacy_level", "private").strip()

    if not all([invite_url, guild_name, guild_id, school_id]):
        return error_json_response(
            [
                "Required fields missing: invite_url, guild_name, guild_id, and school_id are required"
            ],
            status=400,
        )

    # validate privacy_level
    if privacy_level not in ["public", "private"]:
        return error_json_response(
            ["Invalid privacy level. Must be 'public' or 'private'"], status=400
        )

    # both managers and regular users can create any type of invite
    # managers' invites are auto approved, regular users' invites need to be manually approved

    if DiscordInvite.objects.filter(invite_url=invite_url).exists():
        return error_json_response(["This Discord invite has already been submitted"], status=400)

    invite_code = extract_invite_code_from_url(invite_url)
    if invite_code is None:
        return error_json_response(["Invalid Discord invite URL provided"], status=400)

    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return error_json_response(
            [f"Failed to verify Discord server: {invite_result.err}"], status=400
        )

    invite_info = invite_result.val

    # expires_at=null indicates invite is permanent
    if invite_info["expires_at"] is not None:
        return error_json_response(
            [
                "Only permanent Discord invites are allowed. Please create a permanent invite that never expires."
            ],
            status=400,
        )

    if invite_info["guild"]["id"] != guild_id or invite_info["guild"]["name"] != guild_name:
        return error_json_response(
            [
                "Internally validated discord server information does not match what the client provided"
            ],
            status=400,
        )

    if school_id is None:
        return error_json_response(["School selection is required"], status=400)

    school = School.objects.filter(id=int(school_id)).first()
    if school is None:
        return error_json_response(["Invalid school selected"], status=400)

    # validate whether user can access this school
    if discord_user.school != school and not discord_user.is_manager:
        return error_json_response(
            ["You don't have permission to associate servers with this school"], status=400
        )

    subject: Subject | None = None
    if subject_id is not None:
        subject = Subject.objects.filter(id=int(subject_id), schools=school).first()

    course: Course | None = None
    if course_id is not None:
        course = Course.objects.filter(id=int(course_id), subject=subject).first()

    # get instructors if provided
    instructors: list[Instructor] = []
    if instructor_ids:
        # validate that all instructor ids belong to the school and subject
        instructors = list(
            school.instructors.filter(
                id__in=[int(instructor_id) for instructor_id in instructor_ids],
                instruction_entries__course_section__course__subject=subject,
            ).distinct()
        )

    # create server
    privacy_level_enum = (
        DiscordServer.PrivacyLevel.PUBLIC
        if privacy_level == "public"
        else DiscordServer.PrivacyLevel.PRIVATE
    )
    profile = invite_info.get("profile")
    member_count = profile["member_count"] if profile is not None else 0
    datetime_established = get_guild_creation_date(invite_info["guild_id"])

    discord_server, _server_created = DiscordServer.objects.get_or_create(
        server_id=guild_id,
        defaults={
            "name": guild_name,
            "description": invite_info["guild"]["description"] or "",
            "member_count": member_count,
            "icon_url": get_guild_icon_url(guild_id, invite_info["guild"]["icon"]),
            "privacy_level": privacy_level_enum,
            "added_by": discord_user,
            "datetime_established": datetime_established,
        },
    )

    # update server info from discord API for both existing and new servers
    updated_fields: list[str] = []
    if discord_server.name != guild_name:
        discord_server.name = guild_name
        updated_fields.append("name")

    guild_description = invite_info["guild"]["description"] or ""
    if discord_server.description != guild_description:
        discord_server.description = guild_description
        updated_fields.append("description")

    if discord_server.member_count != member_count:
        discord_server.member_count = member_count
        updated_fields.append("member_count")

    new_icon_url = get_guild_icon_url(guild_id, invite_info["guild"]["icon"])
    if discord_server.icon_url != new_icon_url:
        discord_server.icon_url = new_icon_url
        updated_fields.append("icon_url")

    if updated_fields:
        discord_server.save(update_fields=updated_fields)

    max_uses_value = invite_info.get("max_uses", 0)

    # parse expires_at ISO string from discord API
    expires_at_str = invite_info.get("expires_at")
    expires_at_datetime: datetime | None = None
    if expires_at_str is not None:
        expires_at_datetime = parse_datetime(expires_at_str)

    discord_invite = DiscordInvite.objects.create(
        invite_url=invite_url,
        notes_md=notes,
        submitter=discord_user,
        discord_server=discord_server,
        expires_at=expires_at_datetime,
        max_uses=max_uses_value if isinstance(max_uses_value, int) else 0,  # 0 means unlimited
    )

    if not discord_user.is_manager:
        messages.info(
            request,
            "Invite submitted! It will need to be approved by a site admin before it is visible",
        )

    discord_server.schools.add(school)

    if subject is not None:
        discord_server.subjects.add(subject)

    if course is not None:
        discord_server.courses.add(course)

    # add instructor associations
    if instructors:
        discord_server.instructors.add(*instructors)

    success_message = f"Discord invite for '{guild_name}' has been successfully submitted!"
    if discord_invite.is_approved:
        success_message += " It has been automatically approved."

    return interfaces_response.SubmitInviteResponse(
        discord_server=discord_server,
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["GET"])
def get_subjects(request: AuthenticatedRequest, school_id: int) -> HttpResponse:
    school = get_object_or_404(School, id=school_id)
    subjects = list(school.subjects.all().order_by("name"))

    return interfaces_response.GetSubjectsResponse(
        subjects=subjects,
        message="Subjects fetched successfully.",
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["GET"])
def get_courses(request: AuthenticatedRequest, school_id: int, subject_id: int) -> HttpResponse:
    school = get_object_or_404(School, id=school_id)
    subject = get_object_or_404(Subject, id=subject_id)

    courses = list(Course.objects.filter(school=school, subject=subject).order_by("code", "level"))

    return interfaces_response.GetCoursesResponse(
        courses=courses,
        message="Courses fetched successfully.",
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["GET"])
def get_instructors(request: AuthenticatedRequest, school_id: int, subject_id: int) -> HttpResponse:
    school = get_object_or_404(School, id=school_id)
    subject = get_object_or_404(Subject, id=subject_id)

    # get instructors who teach courses in this subject at this school
    instructors = list(
        school.instructors.filter(instruction_entries__course_section__course__subject=subject)
        .distinct()
        .order_by("name")
    )

    return interfaces_response.GetInstructorsResponse(
        instructors=instructors,
        message="Instructors fetched successfully.",
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["PUT"])
def track_invite_usage(request: AuthenticatedRequest, invite_id: int) -> HttpResponse:
    invite = get_object_or_404(DiscordInvite, id=invite_id)

    if not request.user.is_authenticated:
        return error_json_response(["You must log in to track invite usage"], status=401)

    discord_user: DiscordUser = request.user.discord_user  # type: ignore [attr-defined, unused-ignore]

    # check if invite is valid
    if not invite.is_valid or not invite.is_approved:
        return error_json_response(["This invite is no longer valid"], status=400)

    user_ip = request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("HTTP_USER_AGENT", "")

    InviteUsage.objects.create(
        invite=invite,
        used_by=discord_user,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=user_ip,
    )

    invite.uses_count += 1
    invite.save(update_fields=["uses_count"])

    return interfaces_response.BlankResponse().render(request)


@require_roles(required_roles=["manager"], is_api=True)
@require_http_methods(["POST"])
def approve_invite(request: AuthenticatedRequest, invite_id: int) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)
    invite = get_object_or_404(DiscordInvite, id=invite_id)

    if invite.is_approved:
        return error_json_response(["This invite has already been approved"], status=400)

    if not invite.is_valid:
        return error_json_response(["Cannot approve an invalid invite"], status=400)

    # handle invite approval
    invite.approved_by = discord_user
    invite.datetime_approved = timezone.now()

    invite.rejected_by = None
    invite.datetime_rejected = None

    invite.save(
        update_fields=["approved_by", "datetime_approved", "rejected_by", "datetime_rejected"]
    )

    return interfaces_response.BlankResponse().render(request)


@require_roles(required_roles=["manager"], is_api=True)
@require_http_methods(["POST"])
def reject_invite(request: AuthenticatedRequest, invite_id: int) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)
    invite = get_object_or_404(DiscordInvite, id=invite_id)

    if invite.rejected_by is not None:
        return error_json_response(["This invite has already been rejected"], status=400)

    # handle invite rejection
    invite.approved_by = None
    invite.datetime_approved = None

    invite.rejected_by = discord_user
    invite.datetime_rejected = timezone.now()

    invite.save(
        update_fields=["rejected_by", "datetime_rejected", "approved_by", "datetime_approved"]
    )

    return interfaces_response.BlankResponse().render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["GET"])
def get_all_subjects(request: AuthenticatedRequest) -> HttpResponse:
    """Get subjects for server listing search filter"""
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    if discord_user.school is None:
        return error_json_response(["User has no associated school"], status=400)

    subjects = list(
        discord_user.school.subjects.filter(discord_servers__isnull=False)
        .distinct()
        .order_by("name")
    )

    return interfaces_response.GetSubjectsResponse(
        subjects=subjects,
        message="Subjects fetched successfully.",
    ).render(request)


@require_roles(required_roles=None, is_api=True)
@require_http_methods(["GET"])
def get_all_courses(request: AuthenticatedRequest, subject_id: int) -> HttpResponse:
    """Get courses for server listing search filter"""
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    if discord_user.school is None:
        return error_json_response(["User has no associated school"], status=400)

    subject = get_object_or_404(Subject, id=subject_id)
    courses = list(
        Course.objects.filter(school=discord_user.school, subject=subject).order_by("code", "level")
    )

    return interfaces_response.GetCoursesResponse(
        courses=courses,
        message="Courses fetched successfully.",
    ).render(request)


@require_http_methods(["GET"])
def referral_redeem(request: HttpRequest) -> HttpResponse:
    """Store referral code in session for later use during login"""
    referral_code = request.GET.get("referral")

    if referral_code:
        request.session["referral_code"] = referral_code
        return interfaces_response.BlankResponse().render(request)

    return error_json_response(["No referral code provided."], status=400)
