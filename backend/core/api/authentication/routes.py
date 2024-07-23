from django.urls import path

from .views import CheckToken, ForgetPassword, Login, SavePassword, UserPermissions

urlpatterns = [
    path('login/', Login.as_view()),
    path('userPermissions/', UserPermissions.as_view()),
    path('forget/', ForgetPassword.as_view()),
    path('checkToken/', CheckToken.as_view()),
    path('savePassword/', SavePassword.as_view()),
]
