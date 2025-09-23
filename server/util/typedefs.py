from dataclasses import dataclass
from typing import Generic, Literal, NamedTuple, TypeVar

from django.contrib.auth.models import User
from django.http import HttpRequest

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Success(Generic[T]):
    val: T
    ok: Literal[True] = True


@dataclass
class Failure(Generic[E]):
    err: E
    ok: Literal[False] = False


type TResult[E, T] = Success[E] | Failure[T]


class AuthenticatedRequest(HttpRequest):
    user: User


class TPaginationData(NamedTuple):
    current_page: int  # current page number
    total_pages: int  # total number of pages
    has_previous: bool  # whether there's a previous page
    has_next: bool  # whether there's a next page
    previous_page_number: int  # previous page number (or None)
    next_page_number: int  # next page number (or None)
