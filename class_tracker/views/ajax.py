import logging
import time
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from natsort import natsorted
from requests import HTTPError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound as DRFNotFound

from class_tracker.views import interfaces_response
from server.util import bulk_create_and_get

from ..global_search import init_http_retrier
from ..global_search.navigator import (
    get_classlist_result_page,
    get_main_page,
    get_subject_selection_page,
)
from ..global_search.parser import (
    create_careers_and_subjects,
    get_terms_available,
    parse_gs_courses,
    parse_schools,
)
from ..models import (
    ContactInfo,
    Course,
    CourseCareer,
    CourseSection,
    Recipient,
    School,
    Subject,
    Term,
)
from ..util import create_db_courses
from .forms import ContactInfoForm, RecipientForm

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger("main")


RECIPIENT_PREFIX = "recipient"
CONTACT_PREFIX = "contact"
NEW_CONTACT_PREFIX = "contact-new"


@staff_member_required
def get_subjects(request: HttpRequest, school_id: int, term_id: int) -> HttpResponse:
    subjects = Subject.objects.filter(schools__id=school_id, terms__id=term_id)
    return interfaces_response.RespGetSubjects(subjects=list(subjects)).render(request)


@staff_member_required
def refresh_available_terms(request: HttpRequest) -> HttpResponse:
    session = init_http_retrier()

    try:
        main_page_soup = BeautifulSoup(get_main_page(session), "lxml")
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

    return interfaces_response.RespSchoolsTermsUpdate(
        available_schools=schools, available_terms=list(terms), new_terms_count=new_terms_count
    ).render(request)


@staff_member_required
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
            get_subject_selection_page(session, school, term), "lxml"
        )

        _, subjects = create_careers_and_subjects(subjects_page_soup, school, term)

    if school_id == 0:
        subjects = []

    return interfaces_response.RespSubjectsUpdate(available_subjects=subjects).render(request)


@staff_member_required
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
        _ = get_subject_selection_page(session, school, term)

        courses: list[Course] = []
        for career in course_careers:
            for subject in subjects:
                logger.info(
                    " - Parsing courses for %s, %s (%s, %s)",
                    career.name,
                    subject.name,
                    school.name,
                    term.name,
                )

                class_result_soup = BeautifulSoup(
                    get_classlist_result_page(session, career, subject), "lxml"
                )

                gs_courses = parse_gs_courses(class_result_soup)
                courses.extend(create_db_courses(gs_courses, subject, career, school, term))

                time.sleep(0.5)

    return interfaces_response.RespRefreshCourseSections(
        courses=natsorted(courses, key=lambda c: (c.code, c.level))
    ).render(request)


@staff_member_required
@require_http_methods(["GET"])
def get_recipient_form(request: HttpRequest, recipient_id: int) -> HttpResponse:
    recipient: Recipient
    recipient_form: RecipientForm
    contact_info_forms: list[ContactInfoForm] = []

    if recipient_id == 0:
        recipient_form = RecipientForm(prefix=RECIPIENT_PREFIX)
        contact_info_forms = []
    else:
        recipient = Recipient.objects.prefetch_related("phone_numbers").get(id=recipient_id)
        recipient_form = RecipientForm(instance=recipient, prefix=RECIPIENT_PREFIX)
        contact_info_forms = [
            ContactInfoForm(instance=c, prefix=f"{CONTACT_PREFIX}-{c.id}")
            for c in recipient.phone_numbers.all()
        ]

    return interfaces_response.RespGetRecipientForm(
        recipient_form=recipient_form,
        contact_info_forms=contact_info_forms,
        new_contact_info_form=ContactInfoForm(prefix=NEW_CONTACT_PREFIX),
    ).render(request)


@staff_member_required
@require_http_methods(["POST"])
def update_recipient(request: HttpRequest, recipient_id: int) -> HttpResponse:
    if recipient_id == 0:
        # creating new recipient
        recipient = None
        contact_infos: list[ContactInfo] = []
        recipient_form = RecipientForm(request.POST, prefix=RECIPIENT_PREFIX)
        contact_info_forms = []
    else:
        # updating existing recipient
        recipient = Recipient.objects.prefetch_related("phone_numbers").get(id=recipient_id)
        contact_infos = list(recipient.phone_numbers.all())
        recipient_form = RecipientForm(request.POST, instance=recipient, prefix=RECIPIENT_PREFIX)
        contact_info_forms = [
            ContactInfoForm(request.POST, instance=c, prefix=f"{CONTACT_PREFIX}-{c.id}")
            for c in contact_infos
        ]

    new_contact_form = ContactInfoForm(request.POST, prefix=NEW_CONTACT_PREFIX)

    # validate all forms
    forms_valid = recipient_form.is_valid()

    for contact_form in contact_info_forms:
        if not contact_form.is_valid():
            forms_valid = False

    # only validate new contact form if it has data
    new_contact_has_data = new_contact_form.has_changed()
    if new_contact_has_data and not new_contact_form.is_valid():
        forms_valid = False

    if not forms_valid:
        return interfaces_response.RespEditRecipient(
            recipient=None,
            contact_info_forms=contact_info_forms,
            recipient_form=recipient_form,
            new_contact_info_form=new_contact_form,
        ).render(request)

    # save modelforms
    updated_recipient = recipient_form.save()

    updated_contact_infos: list[ContactInfo] = []
    for contact_form in contact_info_forms:
        updated_contact_info = contact_form.save()
        updated_contact_infos.append(updated_contact_info)

    # save new contact info if provided
    if new_contact_has_data:
        new_contact = new_contact_form.save(commit=False)
        new_contact.owner = updated_recipient
        new_contact.save()
        updated_contact_infos.append(new_contact)

    return interfaces_response.RespEditRecipient(
        recipient=Recipient.objects.prefetch_related("phone_numbers").get(id=updated_recipient.id),
        contact_info_forms=None,
        recipient_form=None,
        new_contact_info_form=None,
    ).render(request)


@staff_member_required
@require_http_methods(["POST"])
def add_watched_section(request: HttpRequest, recipient_id: int, section_id: int) -> HttpResponse:
    recipient = Recipient.objects.get(id=recipient_id)
    section = CourseSection.objects.get(id=section_id)

    recipient.watched_sections.add(section)
    return interfaces_response.RespAddWatchedSection(added_section=section).render(request)


@staff_member_required
@require_http_methods(["POST"])
def remove_watched_section(
    request: HttpRequest, recipient_id: int, section_id: int
) -> HttpResponse:
    recipient = Recipient.objects.get(id=recipient_id)
    section = CourseSection.objects.get(id=section_id)

    recipient.watched_sections.remove(section)
    return interfaces_response.BasicResponse(
        is_success=True, message="Section removed successfully"
    ).render(request)
