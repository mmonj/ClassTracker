from typing import TypedDict

from reactivated import interface

from discord_tracker.typedefs.discord_partials import (
    TBaseUserData,
    TChannelData,
    TGameActivity,
    TPrimaryGuildOrClan,
)

TAwareDatetime = str
UUID = str


# guild data returned after retrieving invite data from invite url
class TGuildData(TypedDict):
    id: str
    name: str
    splash: str | None
    banner: str | None
    description: str | None
    icon: str | None
    features: list[str]
    verification_level: int
    vanity_url_code: str | None
    nsfw_level: int
    nsfw: bool
    premium_subscription_count: int


class TGuildProfileData(TypedDict):
    id: str
    name: str
    icon_hash: UUID
    member_count: int
    online_count: int
    description: str | None
    banner_hash: UUID | None
    game_application_ids: list[str]
    game_activity: TGameActivity | None
    tag: str | None
    badge: int
    badge_color_primary: str
    badge_color_secondary: str
    badge_hash: UUID | None
    traits: list[str]
    features: list[str]
    visibility: int
    custom_banner_hash: UUID | None
    premium_subscription_count: int
    premium_tier: int


class TAllauthExtraData(TBaseUserData):
    # collectibles: None
    # display_name_styles: None
    clan: TPrimaryGuildOrClan
    primary_guild: TPrimaryGuildOrClan
    mfa_enabled: bool
    locale: str
    premium_type: int
    email: str
    verified: bool


@interface
class TDiscordInviteData(TypedDict):  # type: ignore [type-var]
    type: int
    code: str
    inviter: TBaseUserData
    expires_at: TAwareDatetime | None  # ISO format (UTC)
    guild: TGuildData
    guild_id: str
    channel: TChannelData
    profile: TGuildProfileData | None
