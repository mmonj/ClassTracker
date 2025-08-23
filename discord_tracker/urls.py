from django.urls import URLPattern, path

from .views import ssr

app_name = "discord_tracker"

ssr_patterns = [
    path("", ssr.index, name="index"),
    path("login/", ssr.login, name="login"),
    path("login-success/", ssr.login_success, name="login_success"),
    path("profile/", ssr.profile, name="profile"),
]

ajax_patterns: list[URLPattern] = []

urlpatterns = ssr_patterns + ajax_patterns
