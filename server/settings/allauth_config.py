"""
Django-allauth config for discord OAuth
https://docs.allauth.org/en/dev/account/configuration.html
"""

import os

from django.urls import reverse_lazy

# django.contrib.sites config for django-allauth to function properly
SITE_ID = 1

# List of authentication backends to use for login
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# list of additional fields required for signup beyond username/email/password (empty means no additional fields)
ACCOUNT_SIGNUP_FIELDS: list[str] = []
# whether django should send additional email verification for regular account signups
ACCOUNT_EMAIL_VERIFICATION = "none"
# list of fields that can be used to log in (eg. username, email)
ACCOUNT_LOGIN_METHODS = ["username"]
# whether email addresses should be unique across all user accounts
ACCOUNT_UNIQUE_EMAIL = False
# the field on the user model to use as the username
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

# whether to automatically create a user account on social login
SOCIALACCOUNT_AUTO_SIGNUP = True
# whether Django should send additional email verification for social account signups
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
# whether oauth flow can be initiated via GET requests to provider login urls
SOCIALACCOUNT_LOGIN_ON_GET = False
# path to the custom adapter for social account logic
SOCIALACCOUNT_ADAPTER = "discord_tracker.util.auth_adapters.DiscordSocialAccountAdapter"
# default protocol for generated URLs
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if os.environ["ENV_TYPE"] != "prod" else "https"

# configuration for the discord OAuth provider
SOCIALACCOUNT_PROVIDERS = {
    "discord": {
        "SCOPE": [
            "identify",
            "email",
        ],
        "AUTH_PARAMS": {"prompt": "none"},
        # whether the email returned by discord should be considered verified
        "VERIFIED_EMAIL": True,
        "APP": {
            "client_id": os.environ["DISCORD_CLIENT_ID"],
            "secret": os.environ["DISCORD_CLIENT_SECRET"],
        },
    }
}

# url to redirect to after successful login
LOGIN_REDIRECT_URL = reverse_lazy("discord_tracker:login_success")
# url to redirect to after logout
LOGOUT_REDIRECT_URL = reverse_lazy("discord_tracker:welcome")
