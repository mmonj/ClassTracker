from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from discord_tracker.models import DiscordUser
from discord_tracker.views import interfaces_response
from discord_tracker.views.forms import SchoolSelectionForm
from server.util.typedefs import AuthenticatedRequest


@login_required
@require_http_methods(["POST"])
def select_school(request: AuthenticatedRequest) -> HttpResponse:
    discord_user = get_object_or_404(DiscordUser, user=request.user)

    form = SchoolSelectionForm(request.POST, instance=discord_user)

    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "School selected successfully!")
        return interfaces_response.SchoolSelectionResponse(
            success=True, message="School selected successfully!"
        ).render(request)

    error_messages = [
        f"{field}: {error}" for field, errors in form.errors.items() for error in errors
    ]

    return interfaces_response.SchoolSelectionResponse(
        success=False,
        message="; ".join(error_messages) if error_messages else "Please correct the form errors.",
    ).render(request)
