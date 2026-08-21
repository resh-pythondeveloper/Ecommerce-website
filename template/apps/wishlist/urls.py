from django.urls import path
from apps.wishlist.views import WishlistView

urlpatterns=[
    path("",WishlistView.as_view()),
    path("<int:variant_id>/",WishlistView.as_view())
]