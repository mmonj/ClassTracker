from typing import TypedDict

from django.http import HttpRequest


class UserInfo(TypedDict):
    name: str
    is_superuser: bool
    is_authenticated: bool


class User(TypedDict):
    user: UserInfo


def user(request: HttpRequest) -> User:
    return {
        "user": {
            "is_superuser": request.user.is_superuser,
            "name": request.user.get_username(),
            "is_authenticated": request.user.is_authenticated,
        }
    }
