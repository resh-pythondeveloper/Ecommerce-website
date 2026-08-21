from django.urls import path

from apps.inventory.views import (
    InventoryView,
    InventoryDetailView,
    InventoryAddStockView,
    InventoryRemoveStockView,
)


urlpatterns = [

    # List all inventory
    path(
        "",
        InventoryView.as_view()
    ),

    # Get / update inventory for variant
    path(
        "variant/<int:variant_id>/",
        InventoryDetailView.as_view()
    ),

    # Add stock
    path(
        "variant/<int:variant_id>/add-stock/",
        InventoryAddStockView.as_view()
    ),

    # Remove stock
    path(
        "variant/<int:variant_id>/remove-stock/",
        InventoryRemoveStockView.as_view()),
]