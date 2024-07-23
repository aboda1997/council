from django.urls import path

from .views import ReceiveStudents, WithdrawStudents

urlpatterns = [
    path('receive/', ReceiveStudents.as_view()),
    path('withdraw/', WithdrawStudents.as_view()),
]
