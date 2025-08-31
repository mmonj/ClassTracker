from typing import TypedDict

from reactivated import interface

TAwareDatetime = str
UUID = str


class TAvatarDecorationData(TypedDict):
    asset: str
    sku_id: str
    expires_at: int | None


class TInviterData(TypedDict):
    id: str
    username: str
    avatar: str
    discriminator: str
    public_flags: int
    flags: int
    banner: str | None
    accent_color: int | None
    global_name: str | None
    avatar_decoration_data: TAvatarDecorationData | None
    banner_color: str | None


# base guild data retrieved via access token (after authenticating via allauth)
class TBaseGuildData(TypedDict):
    id: str
    name: str
    icon: str | None
    banner: str | None
    owner: bool
    permissions: int
    permissions_new: str
    features: list[str]


# guild data returned after retrieving invite data via discord API
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


class TGameActivity(TypedDict):
    pass


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


class TChannelData(TypedDict):
    id: str
    type: int
    name: str


class TGuildAssetUrls(TypedDict):
    icon: str | None
    banner: str | None
    splash: str | None


@interface
class TDiscordInviteData(TypedDict):  # type: ignore [type-var]
    type: int
    code: str
    inviter: TInviterData
    expires_at: TAwareDatetime | None  # ISO format (UTC)
    guild: TGuildData
    guild_id: str
    channel: TChannelData
    profile: TGuildProfileData | None
