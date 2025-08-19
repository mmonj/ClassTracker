from typing import NamedTuple

from reactivated import Pick, template

from discord_tracker.models import DiscordUser


@template
class DiscordTrackerIndex(NamedTuple):
    title: str
    discord_user: (
        Pick[
            DiscordUser,
            "display_name",
            "avatar_url",
            "verified",
            "login_count",
            "first_login",
            "last_login",
        ]
        | None
    )


@template
class DiscordTrackerLogin(NamedTuple):
    title: str
    redirect_url: str
