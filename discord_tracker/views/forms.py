from typing import Any

from django import forms
from django.db import models
from django.utils import timezone

from class_tracker.models import School
from discord_tracker.models import DiscordUser, UserReferral


class SchoolSelectionForm(forms.ModelForm[DiscordUser]):
    class Meta:
        model = DiscordUser
        fields = ["school"]
        widgets = {
            "school": forms.Select(
                attrs={"class": "form-select", "placeholder": "Select your school"}
            )
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        school_field = self.fields["school"]
        school_field.queryset = School.objects.all().order_by("name")  # type: ignore [attr-defined]

        school_field.empty_label = "Select your school..."  # type: ignore [attr-defined]
        school_field.required = True


class DiscordInviteSubmissionForm(forms.Form):
    invite_url = forms.URLField(
        label="Discord Invite URL",
        max_length=200,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://discord.gg/invite-code",
                "required": True,
            }
        ),
        help_text="Enter the full Discord invite URL (e.g., https://discord.gg/abc123 or https://discord.com/invite/abc123)",
    )

    notes = forms.CharField(
        label="Notes (Optional)",
        max_length=511,
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Add any notes about this server (optional)",
            }
        ),
        help_text="Optional notes about the server that will help others understand what it's for",
    )


class ReferralCreationForm(forms.ModelForm[UserReferral]):
    class Meta:
        model = UserReferral
        fields = ["max_uses_choice", "expiry_timeframe"]
        widgets: dict[str, forms.Widget] = {}

    def __init__(
        self, *args: Any, discord_user: "DiscordUser | None" = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.discord_user = discord_user

        self.fields["max_uses_choice"].required = False
        self.fields["max_uses_choice"].label = "Maximum Uses"
        self.fields["max_uses_choice"].help_text = "How many people can use this referral code"

        self.fields["expiry_timeframe"].required = False
        self.fields["expiry_timeframe"].label = "Expiration Timeframe"
        self.fields["expiry_timeframe"].help_text = "How long until this referral code expires"

        # show permanent option to manager users only
        if self.discord_user is not None and self.discord_user.role != DiscordUser.UserRole.MANAGER:
            expiry_choices = [
                choice
                for choice in UserReferral.ExpiryTimeframe.choices
                if choice[0] != UserReferral.ExpiryTimeframe.PERMANENT
            ]
            self.fields["expiry_timeframe"].widget.choices = expiry_choices

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}

        # only manager users can create permanent referrals
        if self.discord_user is not None:
            expiry_timeframe = cleaned_data.get("expiry_timeframe")
            if (
                expiry_timeframe == UserReferral.ExpiryTimeframe.PERMANENT
                and self.discord_user.role != DiscordUser.UserRole.MANAGER
            ):
                raise forms.ValidationError("Only manager users can create permanent referrals.")

        if self.discord_user is not None and not self.discord_user.user.is_superuser:
            max_uses_choice = (
                cleaned_data.get("max_uses_choice") or UserReferral.MaxUsesChoices.TWENTY
            )
            max_uses = int(max_uses_choice)
            max_total_active_uses = 100

            # calc total max_uses for active referrals by this user
            active_referrals_query = UserReferral.objects.filter(created_by=self.discord_user)

            # exclude current instance if updating
            if self.instance.pk is not None:
                active_referrals_query = active_referrals_query.exclude(pk=self.instance.pk)

            active_referrals = active_referrals_query.filter(
                models.Q(datetime_expires__isnull=True)  # never expires
                | models.Q(datetime_expires__gt=timezone.now())  # not yet expired
            ).filter(
                num_uses__lt=models.F("max_uses")  # not fully redeemed
            )

            current_total_max_uses = (
                active_referrals.aggregate(total=models.Sum("max_uses"))["total"] or 0
            )

            new_total = current_total_max_uses + max_uses

            if new_total > max_total_active_uses:
                raise forms.ValidationError(
                    "Cannot create referral. You currently have too many active referrals"
                )

        return cleaned_data
