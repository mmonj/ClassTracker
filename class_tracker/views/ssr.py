import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods

from ..models import Recipient, School, Term
from . import templates

logger = logging.getLogger("main")


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logger.info(
            "User %s is already logged in. Redirecting to homepage index",
            request.user.get_username(),
        )
        return redirect("class_tracker:index")

    if request.method == "GET":
        return templates.TrackerLogin().render(request)

    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is None:
        return templates.TrackerLogin(is_invalid_credentials=True).render(request)

    login(request, user)

    next_url = iri_to_uri(request.POST.get("next", ""))
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return redirect(next_url)

    return redirect("class_tracker:index")


@require_GET
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("class_tracker:login_view")


def index(request: HttpRequest) -> HttpResponse:
    return templates.TrackerIndex(title="Class Tracker").render(request)


@login_required(login_url=reverse_lazy("class_tracker:login_view"))
@staff_member_required
@require_http_methods(["GET", "POST"])
def admin(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    schools = list(School.objects.all())

    return templates.TrackerAdmin(terms_available=terms_available, schools=schools).render(request)


@login_required(login_url=reverse_lazy("class_tracker:login_view"))
@staff_member_required
@require_http_methods(["GET", "POST"])
def add_classes(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    recipients = (
        Recipient.objects.all()
        .prefetch_related(
            "phone_numbers",
            "watched_sections",
            "watched_sections__course",
            "watched_sections__instruction_entries",
            "watched_sections__instruction_entries__instructor",
        )
        .order_by("-datetime_created")
    )

    return templates.TrackerAddClasses(
        terms_available=terms_available, recipients=list(recipients)
    ).render(request)
