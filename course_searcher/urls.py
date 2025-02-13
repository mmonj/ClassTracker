from django.urls import path

from . import views

app_name = "course_searcher"

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view/", views.login_view, name="login_view"),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("admin/", views.admin, name="admin"),
    path("add_classes/", views.add_classes, name="add_classes"),
    path("refresh_available_terms/", views.refresh_available_terms, name="refresh_available_terms"),
    path(
        "refresh_semester_data/<int:school_id>/<int:term_id>/",
        views.refresh_semester_data,
        name="refresh_semester_data",
    ),
    path(
        "refresh_class_data/<int:school_id>/<int:term_id>/<int:subject_id>/",
        views.refresh_class_data,
        name="refresh_class_data",
    ),
]
