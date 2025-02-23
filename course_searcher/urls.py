from django.urls import path

from .views import ssr

app_name = "course_searcher"

urlpatterns = [
    path("", ssr.index, name="index"),
    path("login_view/", ssr.login_view, name="login_view"),
    path("logout_view/", ssr.logout_view, name="logout_view"),
    path("admin/", ssr.admin, name="admin"),
    path("add_classes/", ssr.add_classes, name="add_classes"),
    path("refresh_available_terms/", ssr.refresh_available_terms, name="refresh_available_terms"),
    path(
        "refresh_semester_data/<int:school_id>/<int:term_id>/",
        ssr.refresh_semester_data,
        name="refresh_semester_data",
    ),
    path(
        "refresh_class_data/<int:school_id>/<int:term_id>/<int:subject_id>/",
        ssr.refresh_class_data,
        name="refresh_class_data",
    ),
]
