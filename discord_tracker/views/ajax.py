import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from class_tracker.models import Course, Instructor, School, Subject
from discord_tracker.decorators import roles_required
from discord_tracker.discord.util import (
    extract_invite_code_from_url,
    get_discord_invite_info,
    get_guild_icon_url,
)
from discord_tracker.models import DiscordInvite, DiscordServer, DiscordUser
from discord_tracker.views import interfaces_response
from discord_tracker.views.forms import SchoolSelectionForm
from server.util import error_json_response
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
def validate_discord_invite(request: AuthenticatedRequest) -> HttpResponse:
    """Validate Discord invite and return server info (including existing DB data if server exists)"""
    discord_user: DiscordUser = request.user.discord_user

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
                "Only permanent Discord invites are allowed. Please create a permanent invite that never expires"
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
        available_schools = list(School.objects.all())

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
    instructor_ids = request.POST.getlist("instructor_ids")  # Can be multiple instructors
    privacy_level = request.POST.get("privacy_level", "privileged").strip()

    if not all([invite_url, guild_name, guild_id, school_id]):
        return error_json_response(
            [
                "Required fields missing: invite_url, guild_name, guild_id, and school_id are required"
            ],
            status=400,
        )

    # validate privacy_level
    if privacy_level not in ["public", "privileged"]:
        return error_json_response(
            ["Invalid privacy level. Must be 'public' or 'privileged'"], status=400
        )

    # only managers can create privileged servers
    if privacy_level == "privileged" and not discord_user.is_manager:
        return error_json_response(["Only managers can create privileged servers"], status=400)

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
        else DiscordServer.PrivacyLevel.PRIVILEGED
    )
    discord_server, _server_created = DiscordServer.objects.get_or_create(
        server_id=guild_id,
        defaults={
            "name": guild_name,
            "icon_url": get_guild_icon_url(guild_id, invite_info["guild"]["icon"]),
            "privacy_level": privacy_level_enum,
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

    # add instructor associations
    if instructors:
        discord_server.instructors.add(*instructors)

    success_message = f"Discord invite for '{guild_name}' has been successfully submitted!"
    if discord_invite.is_approved:
        success_message += " It has been automatically approved."

    return interfaces_response.SubmitInviteResponse(
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


@login_required
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
