from django import forms
from django.forms import inlineformset_factory

from ..models import ContactInfo, Recipient


class RecipientForm(forms.ModelForm[Recipient]):
    class Meta:
        model = Recipient
        fields = ["name", "description", "is_contact_by_phone"]
        labels = {
            "is_contact_by_phone": "Allow Contact by Phone",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "description": forms.Textarea(attrs={"placeholder": "Description", "rows": 3}),
        }


class ContactInfoForm(forms.ModelForm[ContactInfo]):
    class Meta:
        model = ContactInfo
        fields = ["number", "is_enabled"]
        labels = {
            "number": "Phone Number",
            "is_enabled": "Enabled",
        }
        widgets = {
            "number": forms.TextInput(attrs={"placeholder": "Phone number"}),
        }


# Create an inline formset for ContactInfo
ContactInfoFormSet = inlineformset_factory(
    Recipient,
    ContactInfo,
    form=ContactInfoForm,
    fields=["number", "is_enabled"],
    extra=1,  # Show 1 empty form by default
    can_delete=True,  # Allow deletion of existing contact info
    can_delete_extra=False,  # Don't show delete checkbox on extra forms
)
