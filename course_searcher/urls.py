from django.urls import path

from . import views

app_name = "course_searcher"

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view/", views.login_view, name="login_view"),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("admin/", views.admin, name="admin"),
    path("add_classes/", views.add_classes, name="add_classes"),
    path(
        "refresh_semester_listing/", views.refresh_semester_listing, name="refresh_semester_listing"
    ),
]
