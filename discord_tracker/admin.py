from django.contrib import admin

from .models import DiscordUser


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin[DiscordUser]):
    list_display = [
        "display_name",
        "username",
        "discord_id",
        "verified",
        "login_count",
        "last_login",
    ]
    list_filter = ["verified", "first_login", "last_login"]
    search_fields = ["username", "global_name", "discord_id"]
    readonly_fields = ["discord_id", "first_login", "last_login", "login_count"]

    fieldsets = [
        (
            "Discord Information",
            {"fields": ["discord_id", "username", "discriminator", "global_name", "avatar"]},
        ),
        ("Account Status", {"fields": ["user", "verified"]}),
        (
            "Login Tracking",
            {"fields": ["first_login", "last_login", "login_count"], "classes": ["collapse"]},
        ),
    ]
