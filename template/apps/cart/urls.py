from django.urls import path

from apps.cart.views import (
    CartView,
    CartItemView,
    CartClearView,
)


urlpatterns = [

    # Get cart / Add item
    path(
        "",
        CartView.as_view(),
    ),

    # Update / Remove cart item
    path(
        "items/<int:item_id>/",
        CartItemView.as_view(),
    ),

    # Clear cart
    path(
        "clear/",
        CartClearView.as_view(),
    ),
]