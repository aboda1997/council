from django.urls import include, path

urlpatterns = [
    path(
        'acceptedStudents/', include('core.services.InitiallyAcceptedStudents.routes')
    ),
    path('universityStudents/', include('core.services.universityStudents.routes')),
    path('graduateStudents/', include('core.services.graduateStudents.routes')),
    path('oldCouncilData/', include('core.services.oldCouncilDataMigration.routes')),
]
