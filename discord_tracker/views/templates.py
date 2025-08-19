from typing import NamedTuple

from reactivated import template


@template
class DiscordTrackerIndex(NamedTuple):
    pass


@template
class DiscordTrackerLogin(NamedTuple):
    title: str
    redirect_url: str
