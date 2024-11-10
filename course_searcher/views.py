import logging
import time

from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods
from requests import HTTPError, Session
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound as DRFNotFound

from . import interfaces, templates
from .global_search.navigator import get_main_page, get_subject_selection_page
from .global_search.parser import create_careers_and_subjects, get_terms_available, parse_schools
from .models import School, Term

logger = logging.getLogger("main")


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logger.info(
            "User %s is already logged in. Redirecting to homepage index",
            request.user.get_username(),
        )
        return redirect("lms_app:home")

    if request.method == "GET":
        return templates.Login().render(request)

    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is None:
        return templates.Login(is_invalid_credentials=True).render(request)

    login(request, user)

    next_url = iri_to_uri(request.POST.get("next", ""))
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return redirect(next_url)

    return redirect("course_searcher:index")


@require_GET
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("course_searcher:login_view")


def index(request: HttpRequest) -> HttpResponse:
    pass


def admin(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    schools = list(set(School.objects.filter(terms__in=terms_available)))
    schools = [School(id=0, name="All", globalsearch_key="-1"), *schools]

    return templates.Admin(
        title="Hello there", terms_available=terms_available, schools=schools
    ).render(request)


def add_classes(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    return templates.AddClasses(title="Hello there", terms_available=terms_available).render(
        request
    )


def refresh_available_terms(request: HttpRequest) -> HttpResponse:
    session = Session()
    soup = BeautifulSoup(get_main_page(session), "html.parser")

    try:
        terms_parsed = get_terms_available(soup)
    except HTTPError as ex:
        raise DRFNotFound([str(ex)]) from ex

    if len(terms_parsed) == 0:
        raise APIException("Parsed 0 terms")

    count = 0
    for term in terms_parsed:
        try:
            term.save()
            count += 1
        except IntegrityError:
            continue

    schools = parse_schools(soup)
    schools.sort(key=lambda school: school.name)

    schools = School.objects.bulk_create(schools, 50, ignore_conflicts=True)
    schools_queryset = School.objects.filter(
        globalsearch_key__in=[f.globalsearch_key for f in schools]
    )

    terms_queryset = Term.objects.all()
    terms_queryset.update(is_available=False)

    terms_queryset = Term.objects.filter(
        name__in=[f.name for f in terms_parsed], year__in=[f.year for f in terms_parsed]
    )
    for term in terms_queryset:
        term.is_available = True
        term.save()
        term.schools.add(*schools_queryset)

    return interfaces.BasicResponse(is_success=True, message=f"{count} new terms created").render(
        request
    )


def refresh_semester_data(request: HttpRequest, school_id: int, term_id: int) -> HttpResponse:
    term = Term.objects.filter(id=term_id).first()
    if term is None:
        raise DRFNotFound([f"Term id {term_id} not found"])

    schools = (
        list(School.objects.prefetch_related("terms").all())
        if school_id == 0
        else [School.objects.prefetch_related("terms").get(id=school_id)]
    )

    for school in schools:
        session = Session()
        subjects_page_soup = BeautifulSoup(
            get_subject_selection_page(session, school, term), "html.parser"
        )

        course_careers, subjects = create_careers_and_subjects(subjects_page_soup, school, term)

        time.sleep(0.5)

    return interfaces.BasicResponse().render(request)
