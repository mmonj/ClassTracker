import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, NamedTuple, cast

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone

from class_tracker.models import CommonModel, Course, Instructor, School, Subject
from server.util.typedefs import Failure, Success, TResult


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


TUserRoleValue = Literal["regular", "manager"]


class DiscordUser(CommonModel):
    class TUserRole(NamedTuple):
        value: TUserRoleValue
        label: str

    # users can refer others, allowing them to login so they can see the invites of servers without needing to also be apart of other required server(s)
    class UserRole(models.TextChoices):
        REGULAR = ("regular", "Regular User")
        MANAGER = ("manager", "Discord Manager")

    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.REGULAR)
    discord_id = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=100)
    discriminator = models.CharField(max_length=10, blank=True)
    global_name = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)

    # if their discord account is verified by email
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)

    first_login = models.DateTimeField(auto_now_add=True, editable=False)
    last_login = models.DateTimeField(auto_now=True, editable=False)
    login_count = models.PositiveIntegerField(default=0, editable=False)

    # OAuth token fields
    access_token = models.TextField(blank=True, editable=False)
    refresh_token = models.TextField(blank=True, editable=False)
    token_expires_at = models.DateTimeField(null=True, blank=True, editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="discord_user")
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
        if self.avatar is not None and self.avatar != "":
            return self.avatar
        # Default Discord avatar based on discriminator or user ID
        if self.discriminator is not None and self.discriminator != "0":
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

    @property
    def is_manager(self) -> bool:
        return self.role == self.UserRole.MANAGER


TServerPrivacyLevelValue = Literal["public", "private"]


class DiscordServer(CommonModel):
    class TServerPrivacyLevel(NamedTuple):
        value: TServerPrivacyLevelValue
        label: str

    class PrivacyLevel(models.TextChoices):
        PUBLIC = ("public", "Public Server")
        PRIVATE = ("private", "Private Server")

    server_id = models.CharField(max_length=64, unique=True, db_index=True)

    name = models.CharField(max_length=255)  # Current server name from Discord API
    icon_url = models.URLField(blank=True)  # Server icon
    member_count = models.PositiveIntegerField(default=0)
    # datetime server was established; default unix time 0 as datetime
    datetime_established = models.DateTimeField(null=True, blank=True)

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

    datetime_last_synced = models.DateTimeField(auto_now_add=True, editable=False)  # last API sync
    is_featured = models.BooleanField(default=False)
    # last date when server info was checked for validity (valid invites)
    last_checked = models.DateField(null=True, blank=True, default=datetime(1970, 1, 1, tzinfo=UTC))

    # should be `initially_added_by`
    added_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, null=True, related_name="added_servers"
    )

    # custom managers
    objects = DiscordServerManager()  # excludes disabled servers
    all_objects = AllDiscordServerManager()  # includes all servers

    class Meta:
        indexes = [
            models.Index(fields=["server_id", "is_featured"]),
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
    notes_md = models.CharField(max_length=255, blank=True)

    # invite status. discord API returns null if invite was created as `unlimited` invite
    expires_at = models.DateTimeField(null=True, blank=True)  # When invite expires
    # if invite was created with no usage limit, discord returns this field as `0`
    max_uses = models.PositiveIntegerField(blank=True, default=0)  # Usage limit
    uses_count = models.PositiveIntegerField(
        default=0, editable=False
    )  # How many times this invite has been used

    # tracks whether the invite is usable (ie. not expired)
    is_valid = models.BooleanField(default=True)

    # DiscordUsers with the `Manager` role can submit invites without the need for approval and approve other invites
    # other users can submit invites as suggestions, but they won't
    # be visible in the discord index page until a manager approves it.
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
    datetime_approved = models.DateTimeField(null=True, blank=True, editable=False)
    datetime_rejected = models.DateTimeField(null=True, blank=True, editable=False)

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


class UserReferral(CommonModel):
    class ExpiryTimeframe(models.TextChoices):
        ONE_WEEK = ("1w", "1 Week")
        TWO_WEEKS = ("2w", "2 Weeks")
        PERMANENT = ("permanent", "Never Expires")

    class MaxUsesChoices(models.TextChoices):
        TWENTY = ("20", "20 Uses")
        FIFTY = ("50", "50 Uses")
        HUNDRED = ("100", "100 Uses")
        UNLIMITED = ("0", "Unlimited Uses")

    _max_uses = 100
    # just inflate the number a ton, works the same as unlimited
    _unlimited_max_uses = _max_uses * 1000

    code = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    max_uses = models.PositiveIntegerField(
        default=1, validators=[MaxValueValidator(_unlimited_max_uses)]
    )
    num_uses = models.PositiveIntegerField(default=0, editable=False)

    datetime_expires = models.DateTimeField(null=True, blank=True)
    expiry_timeframe = models.CharField(
        max_length=20,
        choices=ExpiryTimeframe.choices,
        default=ExpiryTimeframe.ONE_WEEK,
        help_text="Expiry timeframe from creation date",
    )
    max_uses_choice = models.CharField(
        max_length=10,
        choices=MaxUsesChoices.choices,
        default=MaxUsesChoices.TWENTY,
        help_text="Preset options for maximum uses",
    )

    created_by = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, related_name="referrals_created"
    )

    class Meta:
        indexes = [
            models.Index(fields=["created_by"]),
        ]

    def __str__(self) -> str:
        if self.num_uses >= self.max_uses:
            status = "fully redeemed"
        elif self.num_uses > 0:
            status = f"partially redeemed ({self.num_uses}/{self.max_uses})"
        elif self.is_expired():
            status = "expired"
        else:
            status = "pending"
        return f"Referral {self.code} ({status}) by {self.created_by.display_name}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # set max_uses based on max_uses_choice
        if self.max_uses_choice:
            max_uses_value = int(self.max_uses_choice)
            if max_uses_value == 0:
                self.max_uses = self._unlimited_max_uses
            else:
                self.max_uses = max_uses_value

        # only manager users can create permanent referrals
        if (
            self.expiry_timeframe == self.ExpiryTimeframe.PERMANENT
            and self.created_by is not None
            and self.created_by.role != DiscordUser.UserRole.MANAGER
        ):
            raise ValueError("Only manager users can create permanent referrals")

        # only manager users can create unlimited use referrals
        if (
            self.max_uses_choice == self.MaxUsesChoices.UNLIMITED
            and self.created_by is not None
            and self.created_by.role != DiscordUser.UserRole.MANAGER
        ):
            raise ValueError("Only manager users can create unlimited use referrals")

        # datetime_expires based on expiry_timeframe
        if self.expiry_timeframe == self.ExpiryTimeframe.PERMANENT:
            self.datetime_expires = None
        else:
            now = timezone.now()

            if self.expiry_timeframe == self.ExpiryTimeframe.ONE_WEEK:
                self.datetime_expires = now + timedelta(weeks=1)
            elif self.expiry_timeframe == self.ExpiryTimeframe.TWO_WEEKS:
                self.datetime_expires = now + timedelta(weeks=2)

        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return self.datetime_expires is not None and timezone.now() > self.datetime_expires

    def is_valid(self) -> bool:
        return not self.is_expired() and self.num_uses < self.max_uses

    @property
    def is_unlimited(self) -> bool:
        """Check if this referral has unlimited uses."""
        return self.max_uses_choice == self.MaxUsesChoices.UNLIMITED

    def redeem(self, user_target: "DiscordUser") -> TResult[str, str]:
        if not self.is_valid():
            return Failure("Invalid referral code")

        if self.redemptions.filter(redeemed_by=user_target).exists():
            return Failure("You have already redeemed this referral code")

        self.redemptions.create(redeemed_by=user_target)

        self.num_uses += 1
        self.save(update_fields=["num_uses"])

        return Success("Referral code redeemed successfully")

    def revoke(self) -> bool:
        if self.num_uses > 0:
            return False  # Cannot revoke a referral that has already been used

        self.datetime_expires = timezone.now()
        self.save(update_fields=["datetime_expires"])
        return True

    @property
    def url(self) -> str:
        return reverse("discord_tracker:referral_redeem", args=[self.code])


class UserReferralRedemption(CommonModel):
    referral = models.ForeignKey(UserReferral, on_delete=models.CASCADE, related_name="redemptions")
    redeemed_by = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, related_name="referral_redemptions"
    )
    datetime_redeemed = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Referral Redemption: {self.referral.code} by {self.redeemed_by.display_name} at {self.datetime_redeemed}"
