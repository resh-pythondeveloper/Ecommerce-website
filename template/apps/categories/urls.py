from django.urls import path

from apps.categories.views import CategoryView


urlpatterns = [
    path(
        "categories/",
        CategoryView.as_view(),),

    path(
        "categories/<int:id>/",
        CategoryView.as_view(),),
]