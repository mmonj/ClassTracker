from typing import NamedTuple

from reactivated import template


@template
class DiscordTrackerIndex(NamedTuple):
    title: str
