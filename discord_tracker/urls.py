from django.urls import path

from .views import ajax, ssr

app_name = "discord_tracker"

ssr_patterns = [
    path("login/", ssr.login, name="login"),
    path("login-success/", ssr.login_success, name="login_success"),
    path("profile/", ssr.profile, name="profile"),
    path("alerts/", ssr.alerts, name="alerts"),
    path("", ssr.welcome, name="welcome"),
    path("all/", ssr.explore_all_listings, name="explore_all_listings"),
    path("unapproved-invites/", ssr.unapproved_invites, name="unapproved_invites"),
    path("referrals/", ssr.referral_management, name="referral_management"),
    path("referral/<str:referral_code>/", ssr.referral_redeem, name="referral_redeem"),
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
    path(
        "ajax/invites/<int:invite_id>/approve/",
        ajax.approve_invite,
        name="approve_invite",
    ),
    path(
        "ajax/invites/<int:invite_id>/reject/",
        ajax.reject_invite,
        name="reject_invite",
    ),
    path("ajax/subjects/", ajax.get_all_subjects, name="get_all_subjects"),
    path("ajax/subjects/<int:subject_id>/courses/", ajax.get_all_courses, name="get_all_courses"),
    path("ajax/alerts/<int:alert_id>/", ajax.get_alert_details, name="get_alert_details"),
    path(
        "ajax/users/<int:user_id>/alerts/<str:is_read>/",
        ajax.get_user_alerts,
        name="get_user_alerts",
    ),
    path(
        "ajax/alerts/<int:user_alert_id>/mark-as-read/",
        ajax.mark_alert_as_read,
        name="mark_alert_as_read",
    ),
]

urlpatterns = ssr_patterns + ajax_patterns
