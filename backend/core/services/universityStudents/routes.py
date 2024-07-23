from django.urls import path

from .views import StudentsList

urlpatterns = [
    path('studentsList/', StudentsList.as_view()),
]
