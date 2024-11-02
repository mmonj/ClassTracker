from django.urls import path

from . import views

app_name = "course_searcher"

urlpatterns = [
    path("add_classes/", views.add_classes, name="add_classes"),
]
