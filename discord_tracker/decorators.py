from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from discord_tracker.models import DiscordUser


def school_required(
    view_func: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    """
    Decorator to ensure Discord users have selected a school before accessing views.
    Redirects to profile page if user doesn't have a school selected.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest) -> HttpResponse:
        # Skip check for unauthenticated users
        if not request.user.is_authenticated:
            return view_func(request)

        # Check if user has Discord account and school
        try:
            discord_user = DiscordUser.objects.get(user=request.user)
            if discord_user.school is None:
                # Redirect to profile page if no school selected
                return redirect(reverse("discord_tracker:profile"))
        except DiscordUser.DoesNotExist:
            # User doesn't have Discord account, let them proceed
            pass

        return view_func(request)

    return wrapper
