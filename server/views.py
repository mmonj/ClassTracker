from django.http import HttpRequest, HttpResponse

from server import templates


def index(request: HttpRequest) -> HttpResponse:
    return templates.Index().render(request)
