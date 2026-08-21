from django.db import models

from apps.customers.models import CustomerProfile
from apps.products.models import ProductVariant


class Wishlist(models.Model):

    customer = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "wishlists"

    def __str__(self):
        return f"Wishlist - {self.customer.user.email}"


class WishlistItem(models.Model):

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="wishlist_items"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "wishlist_items"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "wishlist",
                    "variant"
                ],
                name="unique_wishlist_variant"
            )
        ]

    def __str__(self):
        return (
            f"{self.wishlist.customer.user.email} "
            f"- {self.variant.sku}"
        )