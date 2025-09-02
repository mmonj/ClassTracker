"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from . import views

ACOUNT_PATHS_REDIRECT_EXCEPTIONS = r"(?:discord/login/|logout/)"

# some allauth paths should not be exposed
redirect_patterns = [
    re_path(
        rf"^accounts/(?!{ACOUNT_PATHS_REDIRECT_EXCEPTIONS}).*$",
        RedirectView.as_view(pattern_name="discord_tracker:login"),
        name="accounts_catch_all_redirect",
    ),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    *redirect_patterns,  # goes before allauth
    path("accounts/", include("allauth.urls")),
    path("class_tracker/", include("class_tracker.urls")),
    path("scheduler/", include("scheduler.urls")),
    path("classcords/", include("discord_tracker.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
