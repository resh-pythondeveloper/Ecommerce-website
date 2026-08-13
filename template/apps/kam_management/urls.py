from django.urls import path
from apps.kam_management.views import KAMCreateAPIView

urlpatterns = [
    path("kam/", KAMCreateAPIView.as_view()),
    path("kam/<int:id>/",KAMCreateAPIView.as_view())
    ]