from django.http import HttpRequest, HttpResponse

from course_searcher.views import interfaces

from ..models import Subject


def get_subjects(request: HttpRequest, school_id: int, term_id: int) -> HttpResponse:
    subjects = Subject.objects.filter(schools__id=school_id, terms__id=term_id)
    return interfaces.RespGetSubjects(subjects=list(subjects)).render(request)
