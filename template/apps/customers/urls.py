from django.urls import path
from apps.customers.views import CustomerCreateAPIView

urlpatterns = [
    path("create/customer/", CustomerCreateAPIView.as_view())
]