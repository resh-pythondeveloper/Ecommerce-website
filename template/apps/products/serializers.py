from django.db import transaction
from rest_framework import serializers
from django.core.exceptions import ValidationError

from apps.products.models import (
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductVariant,
    VariantAttributeValue,
)
from apps.categories.models import Category
from apps.brands.models import Brand
from utils.googledrive.google_cloud import (
    upload_file_to_drive,
    delete_file_from_drive,
)
from apps.products.services import ProductService

class ProductAttributeValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductAttributeValue

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at","is_active"
        ]

    def validate_value(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Attribute value cannot be empty."
            )
        if ProductAttributeValue.objects.filter(
            value__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Attribute Value already exists."
            )

        return value


class ProductAttributeSerializer(serializers.ModelSerializer):

    values = ProductAttributeValueSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ProductAttribute

        fields ="__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at","is_active"
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Attribute name cannot be empty."
            )

        if ProductAttribute.objects.filter(
            name__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Attribute name already exists."
            )

        return value


class VariantAttributeValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = VariantAttributeValue

        fields = [
            "id",
            "attribute",
            "value",
        ]

        read_only_fields = [
            "id",
        ]

    def validate(self, attrs):

        attribute = attrs["attribute"]
        value = attrs["value"]

        # Make sure the value belongs to the selected attribute
        if value.attribute_id != attribute.id:
            raise serializers.ValidationError(
                {
                    "value": (
                        "Selected value does not belong "
                        "to the selected attribute."
                    )
                }
            )

        return attrs


class ProductVariantCreateSerializer(serializers.ModelSerializer):

    attributes = VariantAttributeValueSerializer(
        many=True,
        source="attribute_values",
        required=False
    )

    class Meta:
        model = ProductVariant

        fields = "__all__"

        read_only_fields = [
            "id","sku","is_active","product","is_deleted","created_at","updated_at"
        ]

    def validate_sku(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "SKU cannot be empty."
            )

        return value

    def validate(self, attrs):

        price = attrs.get("price")
        discount_price = attrs.get("discount_price")

        if (
            discount_price is not None
            and price is not None
            and discount_price > price
        ):
            raise serializers.ValidationError(
                {
                    "discount_price": (
                        "Discount price cannot be "
                        "greater than actual price."
                    )
                }
            )

        attributes = attrs.get(
            "attribute_values",
            []
        )

        attribute_ids = [
            item["attribute"].id
            for item in attributes
        ]

        if len(attribute_ids) != len(set(attribute_ids)):
            raise serializers.ValidationError(
                {
                    "attributes": (
                        "The same attribute cannot "
                        "be added more than once."
                    )
                }
            )

        return attrs

class ProductSerializer(serializers.ModelSerializer):
    image=serializers.JSONField(read_only=True)
    product_image=serializers.ImageField(write_only=True,required=False,allow_null=True)

    variants = ProductVariantCreateSerializer(
        many=True,
        required=False
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True
    )

    class Meta:
        model = Product

        fields = "__all__"

        read_only_fields = [
            "id",
            "slug",
            "image",
            "is_deleted",
            "created_at",
            "updated_at",
            "category_name",
            "brand_name","is_active"
        ]

    def validate_category(self, category):

        if category.is_deleted:
            raise serializers.ValidationError(
                "Selected category has been deleted."
            )

        return category

    def validate_brand(self, brand):

        if brand.is_deleted:
            raise serializers.ValidationError(
                "Selected brand has been deleted."
            )


        return brand

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name cannot be empty."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        image_file = validated_data.pop(
            "product_image",
            None
        )

        variants_data = validated_data.pop(
            "variants",
            []
        )

        return ProductService.create_product(
            validated_data=validated_data,
            image_file=image_file,
            variants_data=variants_data,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        image_file = validated_data.pop(
                    "product_image",
                    None)

        variants_data = validated_data.pop(
            "variants",
            None
        )

        return ProductService.update_product(
            product=instance,
            validated_data=validated_data,
            image_file=image_file,
            variants_data=variants_data,
        )
