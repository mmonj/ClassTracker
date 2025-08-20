from django.contrib import admin

from .models import DiscordUser


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin[DiscordUser]):
    list_display = [
        "display_name",
        "get_user_username",
        "get_user_email",
        "get_user_is_active",
        "username",
        "discord_id",
        "verified",
        "login_count",
        "last_login",
    ]
    list_filter = ["verified", "first_login", "last_login", "user__is_active", "user__is_staff"]
    search_fields = ["username", "global_name", "discord_id", "user__username", "user__email"]
    readonly_fields = ["discord_id", "first_login", "last_login", "login_count"]

    fieldsets = [
        (
            "Associated User",
            {"fields": ["user"]},
        ),
        (
            "Discord Information",
            {"fields": ["discord_id", "username", "discriminator", "global_name", "avatar"]},
        ),
        ("Account Status", {"fields": ["verified"]}),
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
