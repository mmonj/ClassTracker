from django.urls import URLPattern, path

from .views import ssr

app_name = "discord_tracker"

ssr_patterns = [
    path("", ssr.index, name="index"),
]

ajax_patterns: list[URLPattern] = []

urlpatterns = ssr_patterns + ajax_patterns
