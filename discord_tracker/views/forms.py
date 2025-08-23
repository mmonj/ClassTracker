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
        if hasattr(school_field, "queryset"):
            school_field.queryset = School.objects.all().order_by("name")
        if hasattr(school_field, "empty_label"):
            school_field.empty_label = "Select your school..."
        school_field.required = True
