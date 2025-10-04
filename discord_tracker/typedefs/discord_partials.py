from typing import TypedDict


class TGameActivity(TypedDict):
    pass


class TPrimaryGuildOrClan(TypedDict):
    identity_guild_id: str
    identity_enabled: bool
    tag: str
    badge: str  # UUID


class TAvatarDecorationData(TypedDict):
    asset: str
    sku_id: str
    expires_at: int | None


class TChannelData(TypedDict):
    id: str
    type: int
    name: str


class TGuildAssetUrls(TypedDict):
    icon: str | None
    banner: str | None
    splash: str | None


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


class TBaseUserData(TypedDict):
    id: str
    username: str | None
    avatar: str | None
    discriminator: str
    public_flags: int
    flags: int
    banner: str | None
    accent_color: int | None
    global_name: str | None
    avatar_decoration_data: TAvatarDecorationData | None
    banner_color: str | None
