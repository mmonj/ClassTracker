from typing import NotRequired, TypedDict

TAwareDatetime = str


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
    clan: None
    primary_guild: None


class TGuildData(TypedDict):
    id: str
    name: str
    splash: None
    banner: None
    description: None
    icon: str | None
    features: list[str]
    verification_level: int
    vanity_url_code: None
    nsfw_level: int
    nsfw: bool
    premium_subscription_count: int


class TChannelData(TypedDict):
    id: str
    type: int
    name: str


class TGuildAssetUrls(TypedDict):
    icon: str | None
    banner: str | None
    splash: str | None


class TDiscordInviteData(TypedDict):
    type: int
    code: str
    inviter: TInviterData
    expires_at: TAwareDatetime | None
    flags: NotRequired[int]
    guild: TGuildData
    guild_id: str
    channel: TChannelData
