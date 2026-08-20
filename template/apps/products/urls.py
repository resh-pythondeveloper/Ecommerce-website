from django.urls import path

from apps.products.views import (
    ProductView,
    ProductAttributeView,
    ProductAttributeValueView,
    ProductAttributeValueDetailView,
    ProductVariantView,
    ProductVariantDetailView,
)


urlpatterns = [

    # PRODUCT

    path(
        "products/",
        ProductView.as_view()),

    path(
        "products/<int:id>/",
        ProductView.as_view()
    ),


    # ==========================================
    # PRODUCT ATTRIBUTE
    # ==========================================

    path(
        "products/attributes/",
        ProductAttributeView.as_view()
    ),

    path(
        "products/attributes/<int:id>/",
        ProductAttributeView.as_view()
    ),


    # ATTRIBUTE VALUES

    path(
        "products/attributes/<int:attribute_id>/values/",
        ProductAttributeValueView.as_view()
    ),

    path(
        "products/attribute-values/<int:id>/",
        ProductAttributeValueDetailView.as_view()
    ),


    # PRODUCT VARIANTS

    path(
        "products/<int:product_id>/variants/",
        ProductVariantView.as_view()
    ),

    path(
        "products/variants/<int:id>/",
        ProductVariantDetailView.as_view()
    ),
]