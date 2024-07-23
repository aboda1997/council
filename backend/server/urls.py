from django.urls import include, path

urlpatterns = [
    path('api/', include('core.api.routes')),
    path('services/', include('core.services.routes')),
]
