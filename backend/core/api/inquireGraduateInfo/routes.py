from django.urls import path

from .views import (
    Filters,
    FormFilters,
    Student,
    StudentHistory,
    StudentsList,
    Attachments,
)

urlpatterns = [
    path("filters/", Filters.as_view()),
    path("formFilters/", FormFilters.as_view()),
    path("student/", Student.as_view()),
    path('studentHistory/', StudentHistory.as_view()),
    path("studentsList/", StudentsList.as_view()),
    path('attachments/', Attachments.as_view()),
]
