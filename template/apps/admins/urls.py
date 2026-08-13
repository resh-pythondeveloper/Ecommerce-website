from django.urls import path
from apps.admins.views import AdminLoginAPIView, AdminOTPVerifyAPIView

urlpatterns = [
    path("Admin/login/", AdminLoginAPIView.as_view()),
    path("Admin/otp-verify/", AdminOTPVerifyAPIView.as_view())
]