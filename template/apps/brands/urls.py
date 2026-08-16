from django.urls import path
from apps.brands.views import BrandView
urlpatterns=[
    path("", BrandView.as_view()),
    path("<int:id>/", BrandView.as_view()),
]