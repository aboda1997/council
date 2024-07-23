from django.urls import include, path

urlpatterns = [
    path(
        'numberAcceptedStudents/',
        include('core.api.reports.numberAcceptedStudents.routes'),
    ),
    path(
        'acceptedStudentsNames/',
        include('core.api.reports.acceptedStudentsNames.routes')),
    path(
        'universityStatusStatistics/',
        include('core.api.reports.universityStatusStatistics.routes'),
        )
]
