from django.urls import path
from apps.vendors.views import VendorAPIView,VendorEmailVerifyView

urlpatterns=[
    path("vendor/",VendorAPIView.as_view()),
    path("vendor/<int:id>/",VendorAPIView.as_view()),
    path("vendor/email/verify/",VendorEmailVerifyView.as_view())
]