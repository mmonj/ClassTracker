import logging

import requests
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from requests import HTTPError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound as DRFNotFound

from . import interfaces
from .global_search_util.parser import get_terms_available, parse_schools
from .models import School, Term
from .templates import AddClasses, Admin

logger = logging.getLogger("main")

GLOBAL_SEARCH_URL = "https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp"


def index(request: HttpRequest) -> HttpResponse:
    pass


def login_view(request: HttpRequest) -> HttpResponse:
    pass


def logout_view(request: HttpRequest) -> HttpResponse:
    pass


def admin(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    return Admin(title="Hello there", terms_available=terms_available).render(request)


def add_classes(request: HttpRequest) -> HttpResponse:
    return AddClasses(title="Hello there").render(request)


def refresh_semester_listing(request: HttpRequest) -> HttpResponse:
    resp = requests.get(GLOBAL_SEARCH_URL, timeout=15)
    if not resp.ok:
        resp.raise_for_status()

    try:
        terms_parsed = get_terms_available(resp.text)
        logger.info(terms_parsed)
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

    schools = parse_schools(resp.text)
    schools = School.objects.bulk_create(schools, 50, ignore_conflicts=True)
    schools_queryset = School.objects.filter(
        globalsearch_key__in=[f.globalsearch_key for f in schools]
    )

    terms_queryset = Term.objects.all()
    for term in terms_queryset:
        term.is_available = False
    Term.objects.bulk_update(terms_queryset, batch_size=100, fields=["is_available"])

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


def refresh_semester_data(request: HttpRequest, semester: str) -> HttpResponse:
    pass
