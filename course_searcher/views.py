from django.http import HttpRequest, HttpResponse

from .templates import AddClasses

def add_classes(request: HttpRequest) -> HttpResponse:
    return AddClasses(title="Hello there").render(request)
