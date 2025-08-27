from django.contrib import admin
from django.http import HttpRequest

from .models import (
    DiscordInvite,
    DiscordServer,
    DiscordUser,
    InviteUsage,
    RequiredDiscordServer,
    UserVouch,
)


class DiscordInviteInline(admin.TabularInline[DiscordInvite, DiscordServer]):
    model = DiscordInvite
    fields = ["invite_url", "notes_md", "expires_at", "max_uses"]
    extra = 1
    show_change_link = True


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin[DiscordUser]):
    list_display = [
        "display_name",
        "get_user_username",
        "get_user_email",
        "get_user_is_active",
        "username",
        "discord_id",
        "school",
        "is_verified",
        "login_count",
        "last_login",
    ]
    list_filter = ["is_verified", "first_login", "last_login", "user__is_active", "user__is_staff"]
    search_fields = ["username", "global_name", "discord_id", "user__username", "user__email"]
    readonly_fields = ["discord_id", "first_login", "last_login", "login_count"]
    list_editable = ["is_verified"]

    fieldsets = [
        (
            "Associated User",
            {"fields": ["user", "school"]},
        ),
        (
            "Discord Information",
            {
                "fields": [
                    "discord_id",
                    "username",
                    "discriminator",
                    "global_name",
                    "avatar",
                    "is_verified",
                    "role",
                ]
            },
        ),
        (
            "Login Tracking",
            {"fields": ["first_login", "last_login", "login_count"], "classes": ["collapse"]},
        ),
    ]

    def get_user_username(self, obj: DiscordUser) -> str:
        """Get the associated Django user's username."""
        return obj.user.username

    get_user_username.short_description = "Django Username"  # type: ignore[attr-defined]

    def get_user_email(self, obj: DiscordUser) -> str:
        """Get the associated Django user's email."""
        return obj.user.email or "(no email)"

    get_user_email.short_description = "Email"  # type: ignore[attr-defined]

    def get_user_is_active(self, obj: DiscordUser) -> bool:
        """Get the associated Django user's active status."""
        return obj.user.is_active

    get_user_is_active.short_description = "Active"  # type: ignore[attr-defined]
    get_user_is_active.boolean = True  # type: ignore[attr-defined]


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin[DiscordServer]):
    list_display = [
        "display_name",
        "name",
        "privacy_level",
        "is_active",
        "is_disabled",
        "get_school_count",
        "get_subject_count",
        "get_course_count",
        "datetime_last_synced",
        "added_by",
    ]
    list_filter = [
        "privacy_level",
        "is_active",
        "is_disabled",
        "datetime_last_synced",
        "schools",
        "subjects",
    ]
    search_fields = ["name", "custom_title", "description", "server_id"]
    readonly_fields = ["datetime_last_synced"]
    list_editable = ["is_active", "is_disabled"]
    filter_horizontal = ["schools", "subjects", "courses", "instructors"]
    inlines = [DiscordInviteInline]

    def get_readonly_fields(
        self, _request: HttpRequest, obj: DiscordServer | None = None
    ) -> list[str]:
        """Make server_id readonly only for existing objects."""
        if obj is not None:  # when existing record
            return [*self.readonly_fields, "server_id"]
        return list(self.readonly_fields)  # when creating new record

    fieldsets = [
        (
            "Server Information",
            {
                "fields": [
                    "server_id",
                    "name",
                    "custom_title",
                    "description",
                    "icon_url",
                ]
            },
        ),
        (
            "Settings",
            {
                "fields": [
                    "privacy_level",
                    "is_active",
                    "is_disabled",
                ]
            },
        ),
        (
            "Academic Associations",
            {
                "fields": [
                    "schools",
                    "subjects",
                    "courses",
                    "instructors",
                ]
            },
        ),
        (
            "Metadata",
            {
                "fields": [
                    "added_by",
                    "datetime_last_synced",
                ]
            },
        ),
    ]

    def get_school_count(self, obj: DiscordServer) -> int:
        """Get the number of associated schools."""
        return obj.schools.count()

    get_school_count.short_description = "Schools"  # type: ignore[attr-defined]

    def get_subject_count(self, obj: DiscordServer) -> int:
        """Get the number of associated subjects."""
        return obj.subjects.count()

    get_subject_count.short_description = "Subjects"  # type: ignore[attr-defined]

    def get_course_count(self, obj: DiscordServer) -> int:
        """Get the number of associated courses."""
        return obj.courses.count()

    get_course_count.short_description = "Courses"  # type: ignore[attr-defined]


@admin.register(DiscordInvite)
class DiscordInviteAdmin(admin.ModelAdmin[DiscordInvite]):
    list_display = [
        "invite_url",
        "discord_server",
        "submitter",
        "is_approved",
        "approved_by",
        "is_valid",
        "expires_at",
        "uses_count",
        "max_uses",
    ]
    list_filter = [
        "is_valid",
        "datetime_approved",
        "expires_at",
        "discord_server__privacy_level",
        "submitter__role",
    ]
    search_fields = [
        "invite_url",
        "discord_server__name",
        "discord_server__custom_title",
        "submitter__username",
        "submitter__global_name",
        "notes_md",
    ]
    readonly_fields = ["uses_count"]
    list_editable = ["is_valid"]

    fieldsets = [
        (
            "Invite Information",
            {
                "fields": [
                    "invite_url",
                    "discord_server",
                    "notes_md",
                ]
            },
        ),
        (
            "Usage & Validity",
            {
                "fields": [
                    "is_valid",
                    "expires_at",
                    "max_uses",
                    "uses_count",
                ]
            },
        ),
        (
            "Approval/Rejection",
            {
                "fields": [
                    "submitter",
                    "approved_by",
                    "datetime_approved",
                    "rejected_by",
                    "datetime_rejected",
                ]
            },
        ),
    ]

    def is_approved(self, obj: DiscordInvite) -> bool:
        """Check if the invite is approved."""
        return obj.is_approved

    is_approved.short_description = "Approved"  # type: ignore[attr-defined]
    is_approved.boolean = True  # type: ignore[attr-defined]


@admin.register(InviteUsage)
class InviteUsageAdmin(admin.ModelAdmin[InviteUsage]):
    list_display = [
        "invite",
        "get_discord_server",
        "used_by",
        "ip_address",
        "datetime_created",
    ]
    list_filter = [
        "datetime_created",
        "invite__discord_server",
        "used_by__role",
    ]
    search_fields = [
        "invite__invite_url",
        "invite__discord_server__name",
        "used_by__username",
        "used_by__global_name",
        "ip_address",
    ]
    readonly_fields = ["datetime_created"]

    fieldsets = [
        (
            "Usage Information",
            {
                "fields": [
                    "invite",
                    "used_by",
                    "datetime_created",
                ]
            },
        ),
        (
            "Tracking Data",
            {
                "fields": [
                    "ip_address",
                    "user_agent",
                ]
            },
        ),
    ]

    def get_discord_server(self, obj: InviteUsage) -> str:
        """Get the Discord server name from the invite."""
        return obj.invite.discord_server.display_name

    get_discord_server.short_description = "Discord Server"  # type: ignore[attr-defined]


@admin.register(RequiredDiscordServer)
class RequiredDiscordServerAdmin(admin.ModelAdmin[RequiredDiscordServer]):
    list_display = [
        "discord_server",
        "get_server_privacy",
        "datetime_created",
    ]
    list_filter = [
        "discord_server__privacy_level",
        "datetime_created",
    ]
    search_fields = [
        "discord_server__name",
        "discord_server__custom_title",
    ]

    fieldsets = [
        (
            "Required Server",
            {
                "fields": [
                    "discord_server",
                ]
            },
        ),
    ]

    def get_server_privacy(self, obj: RequiredDiscordServer) -> str:
        """Get the privacy level of the required server."""
        return obj.discord_server.get_privacy_level_display()

    get_server_privacy.short_description = "Privacy Level"  # type: ignore[attr-defined]


@admin.register(UserVouch)
class UserVouchAdmin(admin.ModelAdmin[UserVouch]):
    list_display = [
        "voucher",
        "vouched_for",
        "get_voucher_role",
        "get_vouched_for_role",
        "datetime_created",
    ]
    list_filter = [
        "voucher__role",
        "vouched_for__role",
        "datetime_created",
    ]
    search_fields = [
        "voucher__username",
        "voucher__global_name",
        "vouched_for__username",
        "vouched_for__global_name",
    ]

    fieldsets = [
        (
            "Vouch Information",
            {
                "fields": [
                    "voucher",
                    "vouched_for",
                    "datetime_created",
                ]
            },
        ),
    ]

    def get_voucher_role(self, obj: UserVouch) -> str:
        """Get the role of the voucher."""
        return obj.voucher.get_role_display()

    get_voucher_role.short_description = "Voucher Role"  # type: ignore[attr-defined]

    def get_vouched_for_role(self, obj: UserVouch) -> str:
        """Get the role of the vouched-for user."""
        return obj.vouched_for.get_role_display()

    get_vouched_for_role.short_description = "Vouched For Role"  # type: ignore[attr-defined]
