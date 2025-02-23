import logging
import time
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods
from requests import HTTPError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound as DRFNotFound

from server.util import bulk_create_and_get

from . import interfaces, templates
from .global_search import init_http_retrier
from .global_search.navigator import (
    get_classlist_result_page,
    get_main_page,
    get_subject_selection_page,
)
from .global_search.parser import (
    create_careers_and_subjects,
    get_terms_available,
    parse_gs_courses,
    parse_schools,
)
from .models import CourseCareer, School, Subject, Term
from .util import create_db_courses

if TYPE_CHECKING:
    from django.db.models import QuerySet

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

    schools = list(School.objects.all())

    return templates.Admin(terms_available=terms_available, schools=schools).render(request)


def add_classes(request: HttpRequest) -> HttpResponse:
    terms_available = list(Term.objects.filter(is_available=True))
    terms_available.sort(key=lambda term: term.year)

    return templates.AddClasses(title="Hello there", terms_available=terms_available).render(
        request
    )


def refresh_available_terms(request: HttpRequest) -> HttpResponse:
    session = init_http_retrier()

    try:
        main_page_soup = BeautifulSoup(get_main_page(session), "html.parser")
    except HTTPError as ex:
        raise DRFNotFound([str(ex)]) from ex

    terms_parsed = get_terms_available(main_page_soup)
    if len(terms_parsed) == 0:
        raise APIException("Parsed 0 terms")

    prev_terms_count = len(Term.objects.all())
    terms = bulk_create_and_get(Term, terms_parsed, fields=["globalsearch_key"])
    new_terms_count = len(Term.objects.all()) - prev_terms_count

    schools = sorted(parse_schools(main_page_soup), key=lambda school: school.name)
    schools = list(bulk_create_and_get(School, schools, fields=["globalsearch_key"]))

    Term.objects.all().update(is_available=False)
    for term in terms:
        term.is_available = True
        term.save(update_fields=["is_available"])
        term.schools.add(*schools)

    return interfaces.RespSchoolsTermsUpdate(
        available_schools=schools, available_terms=list(terms), new_terms_count=new_terms_count
    ).render(request)


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
        session = init_http_retrier()
        subjects_page_soup = BeautifulSoup(
            get_subject_selection_page(session, school, term), "html.parser"
        )

        _, subjects = create_careers_and_subjects(subjects_page_soup, school, term)

    if school_id == 0:
        subjects = []

    return interfaces.RespSubjectsUpdate(available_subjects=subjects).render(request)


def refresh_class_data(
    request: HttpRequest, school_id: int, term_id: int, subject_id: int
) -> HttpResponse:
    schools = (
        list(School.objects.prefetch_related("terms").all())
        if school_id == 0
        else [School.objects.prefetch_related("terms").get(id=school_id)]
    )

    term = Term.objects.get(id=term_id)

    for school in schools:
        logger.info("Processing school: %s", repr(school))

        course_careers = CourseCareer.objects.filter(terms__id=term_id, schools__id=school.id)

        subjects: QuerySet[Subject]
        if subject_id == 0:
            subjects = Subject.objects.filter(terms__id=term_id, schools__id=school.id)
        else:
            subjects = Subject.objects.filter(id=subject_id)

        session = init_http_retrier()
        get_subject_selection_page(session, school, term)

        for career in course_careers:
            for subject in subjects:
                class_result_soup = BeautifulSoup(
                    get_classlist_result_page(session, career, subject), "html.parser"
                )

                gs_courses = parse_gs_courses(class_result_soup)
                create_db_courses(gs_courses, subject, career, school, term)

                time.sleep(0.5)

    return interfaces.BasicResponse().render(request)
