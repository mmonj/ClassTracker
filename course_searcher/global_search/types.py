from dataclasses import dataclass
from typing import Generic, Literal, TypeAlias, TypeVar


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


__all__ = ["Result"]
