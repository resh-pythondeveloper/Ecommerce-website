from django.db import models
from django.utils.text import slugify

class ProductAttribute(models.Model):

    name = models.CharField(
        max_length=100
    )

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        related_name="attributes"
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

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class ProductAttributeValue(models.Model):

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="values"
    )

    value = models.CharField(
        max_length=100
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        "brands.Brand",
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    image = models.JSONField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table="products"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table="productvariant"


class VariantAttributeValue(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="attribute_values"
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.PROTECT,
        related_name="variant_values"
    )

    value = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.PROTECT,
        related_name="variant_values"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "variant",
                    "attribute"
                ],
                name="unique_variant_attribute"
            )
        ]