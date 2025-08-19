import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Check Discord OAuth configuration."""

    help = "Check Discord OAuth configuration and display setup information"

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        self.stdout.write(self.style.SUCCESS("Discord OAuth Configuration Check"))
        self.stdout.write("=" * 50)

        # Check environment variables
        client_id = os.environ.get("DISCORD_CLIENT_ID", "")
        client_secret = os.environ.get("DISCORD_CLIENT_SECRET", "")

        if not client_id:
            self.stdout.write(self.style.ERROR("❌ DISCORD_CLIENT_ID environment variable not set"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ DISCORD_CLIENT_ID: {client_id[:8]}..."))

        if not client_secret:
            self.stdout.write(
                self.style.ERROR("❌ DISCORD_CLIENT_SECRET environment variable not set")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ DISCORD_CLIENT_SECRET: {client_secret[:8]}...")
            )

        # Check Django settings
        self.stdout.write("\n" + self.style.WARNING("Django Settings:"))

        # Check allauth apps
        required_apps = [
            "allauth",
            "allauth.account",
            "allauth.socialaccount",
            "allauth.socialaccount.providers.discord",
            "discord_tracker",
        ]

        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                self.stdout.write(self.style.SUCCESS(f"✅ {app} installed"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ {app} NOT installed"))

        # Check socialaccount settings
        providers = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
        discord_config = providers.get("discord", {})

        if discord_config:
            self.stdout.write(self.style.SUCCESS("✅ Discord provider configured"))
            self.stdout.write(f"   Scopes: {discord_config.get('SCOPE', [])}")
            self.stdout.write(f"   Verified Email: {discord_config.get('VERIFIED_EMAIL', False)}")
        else:
            self.stdout.write(self.style.ERROR("❌ Discord provider NOT configured"))

        # Check redirect URLs
        self.stdout.write("\n" + self.style.WARNING("Redirect URLs:"))
        self.stdout.write(f"LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
        self.stdout.write(f"LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}")

        # Setup instructions
        self.stdout.write("\n" + self.style.WARNING("Setup Instructions:"))
        self.stdout.write("1. Create Discord App at: https://discord.com/developers/applications")
        self.stdout.write("2. Set OAuth2 Redirect URLs:")
        self.stdout.write("   - http://localhost:8000/accounts/discord/login/callback/")
        self.stdout.write("   - https://yourdomain.com/accounts/discord/login/callback/")
        self.stdout.write("3. Set environment variables:")
        self.stdout.write("   - DISCORD_CLIENT_ID=your_client_id")
        self.stdout.write("   - DISCORD_CLIENT_SECRET=your_client_secret")
        self.stdout.write("4. Run migrations: uv run python manage.py migrate discord_tracker")

        if client_id and client_secret:
            self.stdout.write("\n" + self.style.SUCCESS("✅ Configuration looks good!"))
            self.stdout.write("Discord login should be available at: /discords/login/")
        else:
            self.stdout.write("\n" + self.style.ERROR("❌ Please set Discord OAuth credentials"))
