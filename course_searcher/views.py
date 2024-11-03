from django.http import HttpRequest, HttpResponse

from .templates import AddClasses


def index(request: HttpRequest) -> HttpResponse:
    pass


def login_view(request: HttpRequest) -> HttpResponse:
    pass


def logout_view(request: HttpRequest) -> HttpResponse:
    pass


def add_classes(request: HttpRequest) -> HttpResponse:
    return AddClasses(title="Hello there").render(request)
