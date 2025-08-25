from functools import wraps
from typing import Callable, List

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from discord_tracker.models import DiscordUser, TUserRoleValue

TViewCallable = Callable[..., HttpResponse]


def school_required(
    view_func: TViewCallable,
) -> TViewCallable:
    @wraps(view_func)
    def wrapper(request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return view_func(request)

        discord_user = DiscordUser.objects.filter(user__id=request.user.id).first()
        if discord_user is not None and discord_user.school is None:
            return redirect(reverse("discord_tracker:profile"))

        return view_func(request)

    return wrapper


def roles_required(
    *,
    required_roles: List[TUserRoleValue],
) -> Callable[[TViewCallable], TViewCallable]:
    if not required_roles:
        raise ValueError("roles_required decorator requires a non-empty list of roles")

    def decorator(view_func: TViewCallable) -> TViewCallable:
        @wraps(view_func)
        @login_required
        def wrapper(request: HttpRequest) -> HttpResponse:
            # can replace @login_required
            if not request.user.is_authenticated:
                raise PermissionDenied("User is not authenticated")

            discord_user = DiscordUser.objects.filter(user__id=request.user.id).first()
            if discord_user is None:
                raise PermissionDenied("User must have a Discord account linked.")

            if discord_user.role not in required_roles:
                role_names = ", ".join(required_roles)
                raise PermissionDenied(
                    f"You don't have permission to access this feature. Required roles: {role_names}",
                )

            return view_func(request)

        return wrapper

    return decorator
