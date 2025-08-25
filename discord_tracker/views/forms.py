from typing import Any

from django import forms

from class_tracker.models import School
from discord_tracker.models import DiscordUser


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
