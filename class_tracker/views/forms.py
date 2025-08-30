from django import forms

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
