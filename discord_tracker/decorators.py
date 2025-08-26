import logging
from functools import wraps
from typing import Any, Callable, List

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from discord_tracker.models import DiscordUser, TUserRoleValue
from server.util import error_json_response

TViewCallable = Callable[..., HttpResponse]

logger = logging.getLogger("main")


def school_required(
    view_fn: TViewCallable,
) -> TViewCallable:
    @wraps(view_fn)
    def wrapper(request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return view_fn(request)

        discord_user = DiscordUser.objects.filter(user__id=request.user.id).first()
        if discord_user is not None and discord_user.school is None:
            return redirect(reverse("discord_tracker:profile"))

        return view_fn(request)

    return wrapper


def roles_required(
    *,
    required_roles: List[TUserRoleValue],
) -> Callable[[TViewCallable], TViewCallable]:
    if not required_roles:
        raise ValueError("roles_required decorator requires a non-empty list of roles")

    def decorator(view_fn: TViewCallable) -> TViewCallable:
        @wraps(view_fn)
        def wrapper(request: HttpRequest) -> HttpResponse:
            # can replace @login_required
            if not request.user.is_authenticated:
                return redirect("discord_tracker:login")

            discord_user = DiscordUser.objects.filter(user__id=request.user.id).first()
            if discord_user is None:
                return redirect("discord_tracker:login")

            if discord_user.role not in required_roles:
                role_names = ", ".join(required_roles)
                raise PermissionDenied(
                    f"You don't have permission to access this feature. Required roles: {role_names}",
                )

            return view_fn(request)

        return wrapper

    return decorator


def ajax_view(view_fn: TViewCallable) -> TViewCallable:
    @wraps(view_fn)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            return view_fn(request, *args, **kwargs)
        except (ValidationError, PermissionDenied) as e:
            # safe exceptions , ok to expose
            return error_json_response([str(e)], status=400)
        except Exception as e:
            logger.exception("Error in %s", view_fn.__name__)
            if settings.DEBUG:
                # only in dev mode
                return error_json_response([str(e)], status=500)
            # else:
            # for production
            return error_json_response(["Server error"], status=500)

    return wrapper
