import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from class_tracker.models import Course, School, Subject
from discord_tracker.decorators import roles_required
from discord_tracker.discord.util import (
    extract_invite_code_from_url,
    get_discord_invite_info,
    get_guild_icon_url,
)
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser
from discord_tracker.views import interfaces_response
from discord_tracker.views.forms import SchoolSelectionForm
from server.util.typedefs import AuthenticatedRequest

logger = logging.getLogger("main")


@login_required
@require_http_methods(["POST"])
def select_school(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    form = SchoolSelectionForm(request.POST, instance=discord_user)

    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "School selected successfully!")
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


@login_required
@require_http_methods(["GET"])
def server_invites(request: AuthenticatedRequest, server_id: int) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)
    server = get_object_or_404(DiscordServer, id=server_id)

    # check if user can access server
    if not discord_user.can_access_server(server):
        return interfaces_response.ServerInvitesResponse(
            success=False,
            invites=[],
            message="You don't have permission to view invites for this server.",
        ).render(request)

    # get approved invites for this server
    invites = server.invites.filter(
        is_valid=True,
        datetime_approved__isnull=False,
    ).order_by("-datetime_created")

    return interfaces_response.ServerInvitesResponse(
        success=True,
        invites=list(invites),
        message="Invites fetched successfully.",
    ).render(request)


@roles_required(required_roles=["trusted", "manager"])
@require_http_methods(["GET"])
def get_available_schools(request: AuthenticatedRequest) -> HttpResponse:
    """Get available schools based on user role."""
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    available_schools: list[School] = []
    if not discord_user.is_manager and discord_user.school is None:
        raise ValueError("User is not a manager and has no school assigned")

    if not discord_user.is_manager and discord_user.school is not None:
        available_schools = [discord_user.school]
    elif discord_user.is_manager:
        available_schools = list(School.objects.all())

    return interfaces_response.GetAvailableSchoolsResponse(
        success=True,
        available_schools=available_schools,
        message="Available schools fetched successfully.",
    ).render(request)


@roles_required(required_roles=["trusted", "manager"])
@require_http_methods(["POST"])
def submit_invite(request: AuthenticatedRequest) -> HttpResponse:  # noqa: PLR0911, PLR0912
    discord_user: DiscordUser = request.user.discord_user

    invite_url = request.POST.get("invite_url", "").strip()
    notes = request.POST.get("notes", "").strip()
    guild_name = request.POST.get("guild_name", "").strip()
    guild_id = request.POST.get("guild_id", "").strip()
    school_id = request.POST.get("school_id")
    subject_id = request.POST.get("subject_id")
    course_id = request.POST.get("course_id")

    if not all([invite_url, guild_name, guild_id, school_id]):
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="Required fields missing: invite_url, guild_name, guild_id, and school_id are required",
            discord_server=None,
        ).render(request)

    if DiscordInvite.objects.filter(invite_url=invite_url).exists():
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="This Discord invite has already been submitted",
            discord_server=None,
        ).render(request)

    invite_code = extract_invite_code_from_url(invite_url)
    if invite_code is None:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="Invalid Discord invite URL provided",
            discord_server=None,
        ).render(request)

    invite_result = get_discord_invite_info(invite_code)
    if not invite_result.ok:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message=f"Failed to verify Discord server: {invite_result.err}",
            discord_server=None,
        ).render(request)

    invite_info = invite_result.val

    if invite_info["guild"]["id"] != guild_id or invite_info["guild"]["name"] != guild_name:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="Internally validated discord server information does not match what the client provided",
            discord_server=None,
        ).render(request)

    if school_id is None:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="School selection is required",
            discord_server=None,
        ).render(request)

    school = School.objects.filter(id=int(school_id)).first()
    if school is None:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="Invalid school selected",
            discord_server=None,
        ).render(request)

    # validate whether user can access this school
    if discord_user.school != school and not discord_user.is_manager:
        return interfaces_response.SubmitInviteResponse(
            success=False,
            message="You don't have permission to associate servers with this school",
            discord_server=None,
        ).render(request)

    subject: Subject | None = None
    if subject_id is not None:
        subject = Subject.objects.filter(id=int(subject_id), schools=school).first()

    course: Course | None = None
    if course_id is not None:
        course = Course.objects.filter(id=int(course_id), subject=subject).first()

    # create server
    discord_server, _server_created = DiscordServer.objects.get_or_create(
        server_id=guild_id,
        defaults={
            "name": guild_name,
            "icon_url": get_guild_icon_url(guild_id, invite_info["guild"]["icon"]),
            "privacy_level": DiscordServer.PrivacyLevel.PUBLIC,
            "added_by": discord_user,
        },
    )

    # create invite
    discord_invite = DiscordInvite.objects.create(
        invite_url=invite_url,
        notes_md=notes,
        submitter=discord_user,
        discord_server=discord_server,
    )

    discord_server.schools.add(school)

    if subject is not None:
        discord_server.subjects.add(subject)

    if course is not None:
        discord_server.courses.add(course)

    success_message = f"Discord invite for '{guild_name}' has been successfully submitted!"
    if discord_invite.is_approved:
        success_message += " It has been automatically approved."

    return interfaces_response.SubmitInviteResponse(
        success=True,
        message=success_message,
        discord_server=discord_server,
    ).render(request)


@login_required
@require_http_methods(["GET"])
def get_subjects(request: AuthenticatedRequest, school_id: int) -> HttpResponse:
    school = get_object_or_404(School, id=school_id)
    subjects = list(school.subjects.all().order_by("name"))

    return interfaces_response.GetSubjectsResponse(
        subjects=subjects,
        message="Subjects fetched successfully.",
    ).render(request)


@login_required
@require_http_methods(["GET"])
def get_courses(request: AuthenticatedRequest, school_id: int, subject_id: int) -> HttpResponse:
    school = get_object_or_404(School, id=school_id)
    subject = get_object_or_404(Subject, id=subject_id)

    courses = list(Course.objects.filter(school=school, subject=subject).order_by("code", "level"))

    return interfaces_response.GetCoursesResponse(
        courses=courses,
        message="Courses fetched successfully.",
    ).render(request)
