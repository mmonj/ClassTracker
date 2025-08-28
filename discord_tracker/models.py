from typing import Any, Literal, NamedTuple, cast

from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from class_tracker.models import CommonModel, Course, Instructor, School, Subject


class DiscordServerQuerySet(QuerySet["DiscordServer"]):
    def enabled(self) -> "DiscordServerQuerySet":
        return self.filter(is_disabled=False)


class DiscordServerManager(models.Manager["DiscordServer"]):
    """Exclude servers that are disabled"""

    def get_queryset(self) -> DiscordServerQuerySet:
        return DiscordServerQuerySet(self.model, using=self._db).enabled()


class AllDiscordServerManager(models.Manager["DiscordServer"]):
    """Include all servers"""

    def get_queryset(self) -> DiscordServerQuerySet:
        return DiscordServerQuerySet(self.model, using=self._db)


TUserRoleValue = Literal["regular", "trusted", "manager"]


class DiscordUser(CommonModel):
    class TUserRole(NamedTuple):
        value: TUserRoleValue
        label: str

    # trusted or manager DiscordUsers can vouch for users (trust them), allowing them to see the invites of servers without needing to also be apart of other required server(s)
    # 'trusted' role is set as soon as another trusted/manager DiscordUser vouches for them, or if that user is already a member of the required server(s) upon authenticating
    class UserRole(models.TextChoices):
        REGULAR = "regular", "Regular User"
        TRUSTED = "trusted", "Trusted User"
        MANAGER = "manager", "Discord Manager"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="discord_user")
    discord_id = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=100)
    discriminator = models.CharField(max_length=10, blank=True)
    global_name = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)
    # if their discord account is verified by email
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)

    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.REGULAR)

    first_login = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    login_count = models.PositiveIntegerField(default=0)

    # OAuth token fields
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # school that the user is a student of
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.global_name or self.username} ({self.discord_id})"

    @property
    def role_info(self) -> TUserRole:
        return self.TUserRole(cast("TUserRoleValue", self.role), label=self.get_role_display())

    @property
    def display_name(self) -> str:
        return self.global_name or self.username

    @property
    def avatar_url(self) -> str:
        if self.avatar:
            return self.avatar
        # Default Discord avatar based on discriminator or user ID
        if self.discriminator and self.discriminator != "0":
            default_num = int(self.discriminator) % 5
        else:
            default_num = (int(self.discord_id) >> 22) % 6
        return f"https://cdn.discordapp.com/embed/avatars/{default_num}.png"

    @property
    def is_token_expired(self) -> bool:
        """Check if the OAuth access token has expired."""
        if not self.token_expires_at:
            return True
        return timezone.now() >= self.token_expires_at

    @property
    def can_refresh_token(self) -> bool:
        """Check if we have a refresh token available."""
        return bool(self.refresh_token)

    # keep for now, test later if client side can accept UserRole textchoices
    @property
    def is_trusted(self) -> bool:
        return self.role == self.UserRole.TRUSTED

    @property
    def is_manager(self) -> bool:
        return self.role == self.UserRole.MANAGER

    def can_access_server(self, server: "DiscordServer") -> bool:
        if server.privacy_level == DiscordServer.PrivacyLevel.PUBLIC:
            return True
        return self.role_info.value == "trusted" or self.role_info.value == "manager"  # noqa: PLR1714


TServerPrivacyLevelValue = Literal["public", "privileged"]


class DiscordServer(CommonModel):
    class TServerPrivacyLevel(NamedTuple):
        value: TServerPrivacyLevelValue
        label: str

    class PrivacyLevel(models.TextChoices):
        PUBLIC = "public", "Public - visible to all users"
        PRIVILEGED = "privileged", "Privileged - trusted/manager users only"

    server_id = models.CharField(max_length=64, unique=True, db_index=True)

    name = models.CharField(max_length=255)  # Current server name from Discord API
    icon_url = models.URLField(blank=True)  # Server icon

    privacy_level = models.CharField(
        max_length=20, choices=PrivacyLevel.choices, default=PrivacyLevel.PUBLIC
    )

    custom_title = models.CharField(
        max_length=255, blank=True
    )  # override display name; potentially unused
    description = models.TextField(blank=True)  # server description
    is_active = models.BooleanField(default=True)  # to reduce visibility on homepage
    # to allow DiscordManagers to disable/remove servers (defunct servers, etc.)
    is_disabled = models.BooleanField(default=False)

    schools = models.ManyToManyField(School, related_name="discord_servers", blank=True)
    subjects = models.ManyToManyField(Subject, related_name="discord_servers", blank=True)

    courses = models.ManyToManyField(Course, related_name="discord_servers", blank=True)
    instructors = models.ManyToManyField(Instructor, related_name="discord_servers", blank=True)

    datetime_last_synced = models.DateTimeField(auto_now_add=True)  # last API sync
    is_required_for_trust = models.BooleanField(default=False)

    # should be `initially_added_by`
    added_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, null=True, related_name="added_servers"
    )

    # custom managers
    objects = DiscordServerManager()  # excludes disabled servers
    all_objects = AllDiscordServerManager()  # includes all servers

    class Meta:
        indexes = [
            models.Index(fields=["server_id", "is_required_for_trust"]),
        ]

    def __str__(self) -> str:
        return self.custom_title or self.name

    @property
    def privacy_level_info(self) -> TServerPrivacyLevel:
        return self.TServerPrivacyLevel(
            cast("TServerPrivacyLevelValue", self.privacy_level),
            label=self.get_privacy_level_display(),
        )

    @property
    def is_general_server(self) -> bool:
        def has_related(manager: models.Manager[Any]) -> bool:
            qs = manager.all()
            # attempt to avoid further db queries. check if related fields are already prefetched
            if hasattr(qs, "_result_cache") and qs._result_cache is not None:  # noqa: SLF001
                return bool(len(qs._result_cache))  # noqa: SLF001
            # fallback to .exists() (queries db)
            return manager.exists()

        has_courses = has_related(self.courses)
        has_subjects = has_related(self.subjects)
        has_schools = has_related(self.schools)

        return has_schools and not has_subjects and not has_courses

    @property
    def display_name(self) -> str:
        return self.custom_title or self.name


class DiscordInvite(CommonModel):
    invite_url = models.URLField(max_length=200, unique=True, db_index=True)

    # submitter's notes (markdown) about the server
    notes_md = models.CharField(max_length=511, blank=True)

    # invite status. discord API returns null if invite was created as `unlimited` invite
    expires_at = models.DateTimeField(null=True, blank=True)  # When invite expires
    # if invite was created with no usage limit, discord returns this field as `0`
    max_uses = models.PositiveIntegerField(blank=True, default=0)  # Usage limit
    uses_count = models.PositiveIntegerField(default=0)  # How many times this invite has been used

    # tracks whether the invite is usable (ie. not expired)
    is_valid = models.BooleanField(default=True)

    # DiscordUsers with the `Manager` role can submit invites without the need for approval and approve other invites
    # other 'trusted' users can submit invites as suggestions, but they won't
    # be visible in the discord index page until a `Manager` approves it.
    approved_by = models.ForeignKey(
        DiscordUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_invites",
    )
    rejected_by = models.ForeignKey(
        DiscordUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_invites",
    )
    datetime_approved = models.DateTimeField(null=True, blank=True)
    datetime_rejected = models.DateTimeField(null=True, blank=True)

    submitter = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, related_name="submitted_invites"
    )
    discord_server = models.ForeignKey(
        DiscordServer, on_delete=models.CASCADE, related_name="invites"
    )

    class Meta:
        indexes = [
            models.Index(fields=["is_valid", "datetime_approved"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.invite_url} for {self.discord_server.display_name}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # auto approve invite submission if submitter is DiscordManager
        if self.submitter.role == DiscordUser.UserRole.MANAGER and not self.is_approved:
            self.approved_by = self.submitter
            self.datetime_approved = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_approved(self) -> bool:
        return self.approved_by is not None

    @property
    def is_unlimited(self) -> bool:
        return self.expires_at is None


class InviteUsage(CommonModel):
    """track invite uses for analytics"""

    invite = models.ForeignKey(DiscordInvite, on_delete=models.CASCADE, related_name="usages")
    used_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, null=True, related_name="invite_usages"
    )

    # usage tracking for abuse prevention
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["invite", "datetime_created"]),
        ]

    def __str__(self) -> str:
        user_name = self.used_by.display_name if self.used_by else "Anonymous"
        return f"Invite {self.invite.invite_url} used by {user_name}"


class RequiredDiscordServer(CommonModel):
    discord_server = models.ForeignKey(
        DiscordServer, on_delete=models.CASCADE, related_name="required_for_access"
    )

    def __str__(self) -> str:
        return f"Required server: {self.discord_server.display_name}"


class UserVouch(CommonModel):
    """Track when trusted/manager users vouch for regular users"""

    voucher = models.ForeignKey(
        DiscordUser,
        on_delete=models.CASCADE,
        related_name="vouches_given",
        limit_choices_to={"role__in": [DiscordUser.UserRole.TRUSTED, DiscordUser.UserRole.MANAGER]},
    )
    vouched_for = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, related_name="vouches_received"
    )

    class Meta:
        unique_together = ("voucher", "vouched_for")
