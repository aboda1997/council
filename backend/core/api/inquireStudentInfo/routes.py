from django.urls import path

from .views import (
    Filters,
    FormFilters,
    PopupFilters,
    RevertTransaction,
    SecondaryGSInfo,
    Student,
    StudentHistory,
    StudentsList,
    Attachments,
)

urlpatterns = [
    path('filters/', Filters.as_view()),
    path('formFilters/', FormFilters.as_view()),
    path('popupFilters/', PopupFilters.as_view()),
    path('secondaryGSInfo/', SecondaryGSInfo.as_view()),
    path('revertTransaction/', RevertTransaction.as_view()),
    path('student/', Student.as_view()),
    path('studentHistory/', StudentHistory.as_view()),
    path('studentsList/', StudentsList.as_view()),
    path('attachments/', Attachments.as_view()),
]
