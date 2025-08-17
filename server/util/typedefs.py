from dataclasses import dataclass
from typing import Generic, Literal, TypeAlias, TypeVar

from django.contrib.auth.models import User
from django.http import HttpRequest

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Success(Generic[T]):
    value: T
    ok: Literal[True] = True


@dataclass
class Failure(Generic[E]):
    err: E
    ok: Literal[False] = False


Result: TypeAlias = Success[E] | Failure[T]  # noqa: UP040


class AuthenticatedRequest(HttpRequest):
    user: User
