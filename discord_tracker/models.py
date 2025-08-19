from django.contrib.auth.models import User
from django.db import models

from class_tracker.models import CommonModel


class DiscordUser(CommonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="discord_user")
    discord_id = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=100)
    discriminator = models.CharField(max_length=10, blank=True)
    global_name = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)
    verified = models.BooleanField(default=False)

    # Additional tracking fields
    first_login = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    login_count = models.PositiveIntegerField(default=0)

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
