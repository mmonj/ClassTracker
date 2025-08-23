from django.urls import path

from .views import ajax, ssr

app_name = "discord_tracker"

ssr_patterns = [
    path("", ssr.index, name="index"),
    path("login/", ssr.login, name="login"),
    path("login-success/", ssr.login_success, name="login_success"),
    path("profile/", ssr.profile, name="profile"),
]

ajax_patterns = [
    path("ajax/select-school/", ajax.select_school, name="select_school"),
]

urlpatterns = ssr_patterns + ajax_patterns
