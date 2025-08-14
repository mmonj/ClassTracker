from django.urls import path

from class_tracker.views import ajax

from .views import ssr

app_name = "class_tracker"

ssr_urlpatterns = [
    path("", ssr.index, name="index"),
    path("login_view/", ssr.login_view, name="login_view"),
    path("logout_view/", ssr.logout_view, name="logout_view"),
    path("admin/", ssr.admin, name="admin"),
    path("add_classes/", ssr.add_classes, name="add_classes"),
]

ajax_urlpatterns = [
    path("get_subjects/<int:school_id>/<int:term_id>/", ajax.get_subjects, name="get_subjects"),
    path("refresh_available_terms/", ajax.refresh_available_terms, name="refresh_available_terms"),
    path(
        "refresh_semester_data/<int:school_id>/<int:term_id>/",
        ajax.refresh_semester_data,
        name="refresh_semester_data",
    ),
    path(
        "refresh_class_data/<int:school_id>/<int:term_id>/<int:subject_id>/",
        ajax.refresh_class_data,
        name="refresh_class_data",
    ),
    path(
        "get_recipient_form/<int:recipient_id>", ajax.get_recipient_form, name="get_recipient_form"
    ),
    path("add_recipient/<int:recipient_id>", ajax.update_recipient, name="update_recipient"),
    path(
        "add_watched_section/<int:recipient_id>/<int:section_id>/",
        ajax.add_watched_section,
        name="add_watched_section",
    ),
    path(
        "remove_watched_section/<int:recipient_id>/<int:section_id>/",
        ajax.remove_watched_section,
        name="remove_watched_section",
    ),
]


urlpatterns = ssr_urlpatterns + ajax_urlpatterns
