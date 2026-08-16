from django.urls import path
from apps.vendors.views import VendorAPIView,VendorApprovalView

urlpatterns=[
    path("vendor/",VendorAPIView.as_view()),
    path("vendor/<int:id>/",VendorAPIView.as_view()),
    path("vendor/approval/",VendorApprovalView.as_view())
]