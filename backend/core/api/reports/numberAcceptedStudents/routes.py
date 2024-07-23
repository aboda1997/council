from django.urls import path

from .views import Filters, Report

urlpatterns = [
    path('filters/', Filters.as_view()),
    path('report/', Report.as_view()),
]
