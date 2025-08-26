from django.urls import path

from .views import ajax, ssr

app_name = "discord_tracker"

ssr_patterns = [
    path("", ssr.index, name="index"),
    path("login/", ssr.login, name="login"),
    path("login-success/", ssr.login_success, name="login_success"),
    path("profile/", ssr.profile, name="profile"),
    path("unapproved-invites/", ssr.unapproved_invites, name="unapproved_invites"),
]

ajax_patterns = [
    path("ajax/select-school/", ajax.select_school, name="select_school"),
    path("ajax/servers/<int:server_id>/invites/", ajax.server_invites, name="server_invites"),
    path(
        "ajax/validate-discord-invite/",
        ajax.validate_discord_invite,
        name="validate_discord_invite",
    ),
    path("ajax/submit-invite/", ajax.submit_invite, name="submit_invite"),
    path("ajax/schools/<int:school_id>/subjects/", ajax.get_subjects, name="get_subjects"),
    path(
        "ajax/schools/<int:school_id>/subjects/<int:subject_id>/courses/",
        ajax.get_courses,
        name="get_courses",
    ),
    path(
        "ajax/schools/<int:school_id>/subjects/<int:subject_id>/instructors/",
        ajax.get_instructors,
        name="get_instructors",
    ),
    path(
        "ajax/invites/<int:invite_id>/track-usage/",
        ajax.track_invite_usage,
        name="track_invite_usage",
    ),
]

urlpatterns = ssr_patterns + ajax_patterns
