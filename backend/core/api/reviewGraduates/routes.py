from django.urls import path

from .views import Filters, FormFilters, Student, StudentsList, Withdraw

urlpatterns = [
    path("filters/", Filters.as_view()),
    path('formFilters/', FormFilters.as_view()),
    path('student/', Student.as_view()),
    path('withdraw/', Withdraw.as_view()),
    path("studentsList/", StudentsList.as_view()),
]
