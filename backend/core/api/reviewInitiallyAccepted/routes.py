from django.urls import path

from .views import Filters, FormFilters, ReviewStudents, StudentsList

urlpatterns = [
    path("filters/", Filters.as_view()),
    path('formFilters/', FormFilters.as_view()),
    path('reviewStudents/', ReviewStudents.as_view()),
    path("studentsList/", StudentsList.as_view()),
]
