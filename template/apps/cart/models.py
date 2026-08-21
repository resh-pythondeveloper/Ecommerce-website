from django.conf import settings
from django.db import models
from apps.customers.models import CustomerProfile
from apps.products.models import ProductVariant


class Cart(models.Model):

    customer = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart - {self.user.email}"


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "cart_items"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "variant"
                ],
                name="unique_cart_variant"
            )
        ]

    def __str__(self):
        return f"{self.cart.user.email} - {self.variant.sku}"