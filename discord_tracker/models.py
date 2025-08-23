from typing import Any

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from class_tracker.models import CommonModel, Course, Instructor, School, Subject


class DiscordUser(CommonModel):
    # trusted or manager DiscordUsers can vouch for users (trust them), allowing them to see the invites of servers without needing to also be apart of other required server(s)
    # 'trusted' role is set as soon as another trusted/manager DiscordUser vouches for them, or if that user is already a member of the required server(s) upon authenticating
    class UserRole(models.TextChoices):
        REGULAR = "regular", "Regular User"
        TRUSTED = "trusted", "Trusted User"
        MANAGER = "discord_manager", "Discord Manager"

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
        return self.is_trusted or self.is_manager


class DiscordServer(CommonModel):
    class PrivacyLevel(models.TextChoices):
        PUBLIC = "public", "Public - visible to all users"
        PRIVILEGED = "privileged", "Privileged - trusted/manager users only"

    server_id = models.CharField(max_length=64, unique=True, db_index=True)

    name = models.CharField(max_length=255)  # Current server name from Discord API
    icon_url = models.URLField(blank=True)  # Server icon

    privacy_level = models.CharField(
        max_length=20, choices=PrivacyLevel.choices, default=PrivacyLevel.PUBLIC
    )

    custom_title = models.CharField(max_length=255, blank=True)  # Override display name
    description = models.TextField(blank=True)  # Admin-provided description
    is_active = models.BooleanField(default=True)  # to reduce visibility on homepage
    # to allow DiscordManagers to disable/remove servers (defunct servers, etc.)
    is_disabled = models.BooleanField(default=False)

    schools = models.ManyToManyField(School, related_name="discord_servers", blank=True)
    subjects = models.ManyToManyField(Subject, related_name="discord_servers", blank=True)

    courses = models.ManyToManyField(Course, related_name="discord_servers", blank=True)
    instructors = models.ManyToManyField(Instructor, related_name="discord_servers", blank=True)

    datetime_last_synced = models.DateTimeField(null=True, blank=True)  # Last API sync
    added_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, null=True, related_name="added_servers"
    )

    def __str__(self) -> str:
        return self.custom_title or self.name

    @property
    def is_general_server(self) -> bool:
        return not self.courses.exists() and (self.subjects.exists() or self.schools.exists())

    @property
    def display_name(self) -> str:
        return self.custom_title or self.name


class DiscordInvite(CommonModel):
    invite_url = models.URLField(max_length=200, unique=True, db_index=True)

    notes_md = models.CharField(max_length=511, blank=True)  # Submitter's notes about the server

    # invite status. discord API returns null if invite was created as `unlimited` invite
    expires_at = models.DateTimeField(null=True, blank=True)  # When invite expires
    # if invite was created with no usage limit, discord returns this field as `0`
    max_uses = models.PositiveIntegerField(blank=True, default=0)  # Usage limit
    uses_count = models.PositiveIntegerField(default=0)  # How many times this invite has been used

    # Validation tracking
    is_valid = models.BooleanField(default=True)

    # DiscordUsers with the `DiscordManager` role can submit invites without the need for approval.
    # Allow DiscordUsers that have the 'DiscordManager' role to approve invites.
    # DiscordUser users who don't have the `DiscordManager` role can submit invites as suggestions, but they won't
    # be visible in the discord index page until a `DiscordManager` approves it.
    approved_by = models.ForeignKey(
        DiscordUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_invites",
    )
    datetime_approved = models.DateTimeField(null=True, blank=True)

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


class InviteUsage(CommonModel):
    """Track who used which invites (for analytics)."""

    invite = models.ForeignKey(DiscordInvite, on_delete=models.CASCADE, related_name="usages")
    used_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, null=True, related_name="invite_usages"
    )

    # Usage tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # For abuse prevention
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
