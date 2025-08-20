import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods

from ..models import ClassAlert, Recipient, School, Term
from . import templates
from .typedefs import TPaginationData

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
        return templates.ClassTrackerLogin().render(request)

    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    # only allow login if user has a usable password
    if user is None or not user.has_usable_password():
        return templates.ClassTrackerLogin(is_invalid_credentials=True).render(request)

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
    return templates.ClassTrackerIndex(title="Class Tracker").render(request)


@login_required(login_url=reverse_lazy("class_tracker:login_view"))
@staff_member_required
@require_http_methods(["GET", "POST"])
def manage_course_list(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    schools = list(School.objects.all())

    return templates.ClassTrackerManageCourselist(
        terms_available=terms_available, schools=schools
    ).render(request)


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

    return templates.ClassTrackerAddClasses(
        terms_available=terms_available, recipients=list(recipients)
    ).render(request)


@login_required(login_url=reverse_lazy("class_tracker:login_view"))
@staff_member_required
@require_http_methods(["GET"])
def view_class_alerts(request: HttpRequest) -> HttpResponse:
    page = request.GET.get("page", 1)
    recipient_id = request.GET.get("recipient_id", 0)

    try:
        page = int(page)
        recipient_id = int(recipient_id)
    except (ValueError, TypeError):
        page = 1
        recipient_id = 0

    # recipients for dropdown filter
    recipients = list(Recipient.objects.all().order_by("name"))

    # base queryset if no recipient filter applied
    alerts_queryset = (
        ClassAlert.objects.select_related(
            "recipient",
            "course_section",
            "course_section__course",
            "course_section__course__subject",
            "course_section__term",
        )
        .prefetch_related(
            "course_section__instruction_entries__days",
            "course_section__instruction_entries__instructor",
        )
        .order_by("-datetime_created")
    )

    if recipient_id > 0:
        alerts_queryset = alerts_queryset.filter(recipient_id=recipient_id)

    page_size = 50
    paginator = Paginator(alerts_queryset, page_size)
    page_obj = paginator.get_page(page)

    pagination_data = TPaginationData(
        current_page=page_obj.number,
        total_pages=paginator.num_pages,
        has_previous=page_obj.has_previous(),
        has_next=page_obj.has_next(),
        previous_page_number=page_obj.previous_page_number() if page_obj.has_previous() else 0,
        next_page_number=page_obj.next_page_number() if page_obj.has_next() else 0,
    )

    return templates.ClassTrackerClassAlerts(
        title="Class Alerts",
        class_alerts=list(page_obj.object_list),
        recipients=recipients,
        selected_recipient_id=recipient_id,
        pagination=pagination_data,
    ).render(request)
