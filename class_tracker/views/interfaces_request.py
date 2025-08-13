from typing import NamedTuple

from reactivated import interface

from .forms import RecipientForm


class TRecipientFullForm(NamedTuple):
    recipient_id: int
    recipient_form: RecipientForm


@interface
class TrackerReqAddPersons(NamedTuple):
    recipients: list[TRecipientFullForm]
