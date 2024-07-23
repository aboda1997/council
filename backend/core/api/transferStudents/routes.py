from django.urls import path

from core.api.transferStudents.views import Filters, FormFilters, Student

from .views import Attachments, FacultyData, StudentsList, Transfer

urlpatterns = [
    path('student/', Student.as_view()),
    path("studentsList/", StudentsList.as_view()),
    path("filters/", Filters.as_view()),
    path('formFilters/', FormFilters.as_view()),
    path('facultyData/', FacultyData.as_view()),
    path('transfer/', Transfer.as_view()),
    path('attachments/', Attachments.as_view()),
]
