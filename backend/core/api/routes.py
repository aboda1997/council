from django.urls import include, path

urlpatterns = [
    path('authentication/', include('core.api.authentication.routes')),
    path('uploadCDFile/', include('core.api.uploadCDFile.routes')),
    path('inquireCDStudent/', include('core.api.inquireCDStudent.routes')),
    path('inquireStudentInfo/', include('core.api.inquireStudentInfo.routes')),
    path('militaryEducation/', include('core.api.militaryEducation.routes')),
    path('reviewGraduates/', include('core.api.reviewGraduates.routes')),
    path(
        'reviewInitiallyAccepted/', include('core.api.reviewInitiallyAccepted.routes')
    ),
    path('transferStudents/', include('core.api.transferStudents.routes')),
    path('inquireGraduateInfo/', include('core.api.inquireGraduateInfo.routes')),
    path('', include('core.api.reports.routes')),
]
