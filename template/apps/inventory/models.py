from django.db import models
from apps.products.models import ProductVariant


class Inventory(models.Model):

    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="inventory"
    )

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    reserved_quantity = models.PositiveIntegerField(
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5
    )

    reorder_quantity = models.PositiveIntegerField(
        default=10
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "inventory"

    def __str__(self):
        return f"{self.variant.sku} - {self.available_quantity}"

    @property
    def available_quantity(self):
        return max(
            self.stock_quantity - self.reserved_quantity,
            0
        )

    @property
    def is_low_stock(self):
        return (
            self.available_quantity
            <= self.low_stock_threshold
        )