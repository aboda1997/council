from django.urls import path

from .views import CDStudent, CDStudentsList, Filters, GSFilters

urlpatterns = [
    path('student/', CDStudent.as_view()),
    path('list/', CDStudentsList.as_view()),
    path('filters/', Filters.as_view()),
    path('gsFilters/', GSFilters.as_view()),
]
