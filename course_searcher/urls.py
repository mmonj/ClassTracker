from django.urls import path

from . import views

app_name = "course_searcher"

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view/", views.login_view, name="login_view"),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("add_classes/", views.add_classes, name="add_classes"),
]
