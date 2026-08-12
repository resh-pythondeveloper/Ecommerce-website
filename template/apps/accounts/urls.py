from django.urls import path

from apps.accounts.views import RegisterView,VerifyEmailView,ResendOTPView,LoginView,RefreshTokenAPIView,LogoutView

urlpatterns = [
    path("register/",RegisterView.as_view()),
    path("verify-email/",VerifyEmailView.as_view()),
    path("resend-otp/",ResendOTPView.as_view()),
    path("login/",LoginView.as_view()),

    path("refresh/",RefreshTokenAPIView.as_view()),
    path("logout/",LogoutView.as_view(),),

]