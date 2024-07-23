from django.urls import path

from .views import ReceiveStudents, RepeatedRecords, WithdrawStudents

urlpatterns = [
    path('send/', ReceiveStudents.as_view()),
    path('withdraw/', WithdrawStudents.as_view()),
    path('repeatedRecords/', RepeatedRecords.as_view()),
]
