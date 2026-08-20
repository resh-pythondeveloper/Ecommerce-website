from django.db import transaction
from django.utils.text import slugify
from apps.products.models import (
    Product,
    ProductVariant,
    VariantAttributeValue,
)

from utils.googledrive.google_cloud import (
    upload_file_to_drive,
    delete_file_from_drive,
)


class ProductService:

    @staticmethod
    @transaction.atomic
    def create_product(
        *,
        validated_data,
        image_file=None,
        variants_data=None,
    ):

        variants_data = variants_data or []

        # -------------------------
        # Create product
        # -------------------------

        product = Product.objects.create(
            **validated_data
        )

        # -------------------------
        # Upload product image
        # -------------------------

        if image_file:

            image_data = upload_file_to_drive(
                file=image_file,
                entity_type="Products",
                folder_name=product.name,
            )

            product.image = image_data

            product.save(
                update_fields=["image"]
            )

        # -------------------------
        # Create variants
        # -------------------------

        for variant_data in variants_data:

            attributes_data = variant_data.pop(
                "attribute_values",
                []
            )

            variant = ProductVariant.objects.create(
                product=product,
                **variant_data
            )

            ProductService._create_variant_attributes(
                variant=variant,
                product=product,
                attributes_data=attributes_data,
            )

        return product

    @staticmethod
    @transaction.atomic
    def update_product(
        *,
        product,
        validated_data,
        image_file=None,
        variants_data=None,
    ):

        # -------------------------
        # Update product fields
        # -------------------------

        for field, value in validated_data.items():

            setattr(
                product,
                field,
                value
            )

        product.save()

        # -------------------------
        # Replace image
        # -------------------------

        if image_file:

            ProductService._replace_image(
                product=product,
                image_file=image_file,
            )

        # -------------------------
        # Update variants
        # -------------------------

        if variants_data is not None:

            for variant_data in variants_data:

                attributes_data = variant_data.pop(
                    "attribute_values",
                    []
                )

                variant_id = variant_data.pop(
                    "id",
                    None
                )

                # Existing variant
                if variant_id:

                    variant = ProductVariant.objects.filter(
                        id=variant_id,
                        product=product,
                        is_deleted=False,
                    ).first()

                    if not variant:
                        raise ValueError(
                            f"Variant {variant_id} "
                            "does not exist."
                        )

                    for field, value in variant_data.items():

                        setattr(
                            variant,
                            field,
                            value
                        )

                    variant.save()

                    if attributes_data:

                        variant.attribute_values.all().delete()

                        ProductService._create_variant_attributes(
                            variant=variant,
                            product=product,
                            attributes_data=attributes_data,
                        )

                # New variant
                else:

                    variant = ProductVariant.objects.create(
                        product=product,
                        **variant_data
                    )

                    ProductService._create_variant_attributes(
                        variant=variant,
                        product=product,
                        attributes_data=attributes_data,
                    )

        return product

    @staticmethod
    def _create_variant_attributes(
        *,
        variant,
        product,
        attributes_data,
    ):

        for attribute_data in attributes_data:

            attribute = attribute_data["attribute"]

            value = attribute_data["value"]

            # Attribute belongs to product category
            if (
                attribute.category_id
                != product.category_id
            ):
                raise ValueError(
                    f"Attribute '{attribute.name}' "
                    "does not belong to the "
                    "product category."
                )

            # Value belongs to attribute
            if (
                value.attribute_id
                != attribute.id
            ):
                raise ValueError(
                    f"Value '{value.value}' "
                    f"does not belong to "
                    f"attribute '{attribute.name}'."
                )

            VariantAttributeValue.objects.create(
                variant=variant,
                attribute=attribute,
                value=value,
            )

    @staticmethod
    def _replace_image(
        *,
        product,
        image_file,
    ):

        # Delete old Google Drive image
        if product.image:

            old_file_id = product.image.get(
                "file_id"
            )

            if old_file_id:

                delete_file_from_drive(
                    old_file_id
                )

        # Upload new image
        image_data = upload_file_to_drive(
            file=image_file,
            entity_type="Products",
            folder_name=product.name,
        )

        product.image = image_data

        product.save(
            update_fields=["image"]
        )

    @staticmethod
    @transaction.atomic
    def delete_product(product):

        # -------------------------
        # Delete Google Drive image
        # -------------------------

        if product.image:

            file_id = product.image.get(
                "file_id"
            )

            if file_id:

                delete_file_from_drive(
                    file_id
                )

        # -------------------------
        # Soft delete product
        # -------------------------

        product.is_deleted = True
        product.is_active = False

        product.save(
            update_fields=[
                "is_deleted",
                "is_active",
            ]
        )

        # -------------------------
        # Soft delete variants
        # -------------------------

        product.variants.update(
            is_deleted=True,
            is_active=False,
        )

        return product

    @staticmethod
    def generate_variant_sku(product, attributes_data):

        # Product part
        product_code = slugify(
            product.name
        ).upper().replace("-", "")[:10]

        attribute_codes = []

        for attribute_data in attributes_data:

            attribute = attribute_data["attribute"]
            value = attribute_data["value"]

            # Example:
            # Size + L
            # Color + Blue
            value_code = slugify(
                value.value
            ).upper().replace("-", "")

            attribute_codes.append(
                value_code
            )

        # Example:
        # NIKETSHIRT-L-BLUE

        sku = "-".join(
            [
                product_code,
                *attribute_codes
            ]
        )

        # Check duplicate
        original_sku = sku
        counter = 1

        while ProductVariant.objects.filter(
            sku=sku
        ).exists():
            counter += 1

            sku = f"{original_sku}-{counter}"

        return sku
