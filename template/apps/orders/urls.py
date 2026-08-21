from django.urls import path

from apps.orders.views import (
    OrderCreateAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)


urlpatterns = [

    path(
        "",
        OrderListAPIView.as_view(),
    ),

    path(
        "create/",
        OrderCreateAPIView.as_view(),
    ),

    path(
        "<int:pk>/",
        OrderDetailAPIView.as_view(),
    ),
]