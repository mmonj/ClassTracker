"""
django-allauth config for discord OAuth
"""

import os

from django.urls import reverse_lazy

# django.contrib.sites config for django-allauth to function properly
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"  # email verification done through Discord
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD: str | None = None

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_ADAPTER = "discord_tracker.util.auth_adapters.DiscordSocialAccountAdapter"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if os.environ["ENV_TYPE"] != "prod" else "https"

SOCIALACCOUNT_PROVIDERS = {
    "discord": {
        "SCOPE": [
            "identify",
            "email",
            "guilds",
        ],  # permissions for Discord API
        "AUTH_PARAMS": {"prompt": "none"},
        "VERIFIED_EMAIL": True,
        "APP": {
            "client_id": os.environ["DISCORD_CLIENT_ID"],
            "secret": os.environ["DISCORD_CLIENT_SECRET"],
        },
    }
}

LOGIN_REDIRECT_URL = reverse_lazy("discord_tracker:login_success")
LOGOUT_REDIRECT_URL = reverse_lazy("discord_tracker:welcome")
