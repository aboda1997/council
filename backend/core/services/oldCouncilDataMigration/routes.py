from django.urls import path

from .views import getRepeatedStudents, getStudentsByFaculty, updateInvalidStudents

urlpatterns = [
    path("transferStudents/", getStudentsByFaculty.as_view()),
    path("repeatedStudents/", getRepeatedStudents.as_view()),
    path("updateStudents/", updateInvalidStudents.as_view()),
]
