from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.products.models import Product,ProductAttribute,ProductAttributeValue,ProductVariant,VariantAttributeValue
from apps.products.serializers import ProductSerializer,ProductAttributeSerializer,ProductAttributeValueSerializer,ProductVariantCreateSerializer
from apps.products.services import ProductService


class ProductView(APIView):

    # ==========================================
    # CREATE PRODUCT
    # ==========================================

    def post(self, request):

        serializer = ProductSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Product created successfully",
                "data": ProductSerializer(
                    product
                ).data,
            },
            status=status.HTTP_201_CREATED
        )

    # ==========================================
    # GET PRODUCTS / SINGLE PRODUCT
    # ==========================================

    def get(self, request, id=None):

        # --------------------------------------
        # Single product
        # --------------------------------------

        if id:

            product = get_object_or_404(
                Product,
                id=id,
                is_deleted=False
            )

            serializer = ProductSerializer(
                product
            )

            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        # --------------------------------------
        # Product list
        # --------------------------------------

        products = Product.objects.filter(
            is_deleted=False
        ).select_related(
            "category",
            "brand"
        ).prefetch_related(
            "variants__attribute_values__attribute",
            "variants__attribute_values__value",
        ).order_by(
            "-created_at"
        )

        # --------------------------------------
        # Customer sees active products only
        # --------------------------------------

        # if request.user.role == "CUSTOMER":

        #     products = products.filter(
        #         is_active=True
        #     )

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": products.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # UPDATE PRODUCT
    # ==========================================

    def patch(self, request, id=None):

        product = get_object_or_404(
            Product,
            id=id,
            is_deleted=False
        )

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Product updated successfully",
                "data": ProductSerializer(
                    product
                ).data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # DELETE PRODUCT
    # ==========================================

    def delete(self, request, id=None):

        product = get_object_or_404(
            Product,
            id=id,
            is_deleted=False
        )

        ProductService.delete_product(
            product
        )

        return Response(
            {
                "success": True,
                "message": "Product deleted successfully",
            },
            status=status.HTTP_200_OK
        )

class ProductAttributeView(APIView):

    # ==========================================
    # CREATE ATTRIBUTE
    # ==========================================

    def post(self, request):

        serializer = ProductAttributeSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        attribute = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Product attribute created successfully",
                "data": ProductAttributeSerializer(
                    attribute
                ).data,
            },
            status=status.HTTP_201_CREATED
        )

    # ==========================================
    # LIST / DETAIL
    # ==========================================

    def get(self, request, id=None):

        if id:

            attribute = get_object_or_404(
                ProductAttribute,
                id=id
            )

            serializer = ProductAttributeSerializer(
                attribute
            )

            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        attributes = ProductAttribute.objects.filter(
            is_active=True
        ).select_related(
            "category"
        ).prefetch_related(
            "values"
        ).order_by(
            "-created_at"
        )

        serializer = ProductAttributeSerializer(
            attributes,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": attributes.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # UPDATE
    # ==========================================

    def patch(self, request, id=None):

        attribute = get_object_or_404(
            ProductAttribute,
            id=id
        )

        serializer = ProductAttributeSerializer(
            attribute,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        attribute = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Product attribute updated successfully",
                "data": ProductAttributeSerializer(
                    attribute
                ).data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # DELETE
    # ==========================================

    def delete(self, request, id=None):

        attribute = get_object_or_404(
            ProductAttribute,
            id=id
        )

        attribute.is_active = False
        attribute.save(
            update_fields=["is_active"]
        )

        return Response(
            {
                "success": True,
                "message": "Product attribute deleted successfully",
            },
            status=status.HTTP_200_OK
        )

class ProductAttributeValueView(APIView):

    def post(self, request, attribute_id):

        attribute = get_object_or_404(
            ProductAttribute,
            id=attribute_id,
            is_active=True
        )

        data = request.data.copy()
        data["attribute"] = attribute.id

        serializer = ProductAttributeValueSerializer(
            data=data
        )

        serializer.is_valid(
            raise_exception=True
        )

        value = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Attribute value created successfully",
                "data": ProductAttributeValueSerializer(
                    value
                ).data,
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request, attribute_id):

        attribute = get_object_or_404(
            ProductAttribute,
            id=attribute_id,
            is_active=True
        )

        values = ProductAttributeValue.objects.filter(
            attribute=attribute,
            is_active=True
        ).order_by("value")

        serializer = ProductAttributeValueSerializer(
            values,
            many=True
        )

        return Response(
            {
                "success": True,
                "attribute": attribute.name,
                "count": values.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

class ProductAttributeValueDetailView(APIView):

    # ==========================================
    # UPDATE VALUE
    # ==========================================

    def patch(self, request, id):

        value = get_object_or_404(
            ProductAttributeValue,
            id=id
        )

        serializer = ProductAttributeValueSerializer(
            value,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        value = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Attribute value updated successfully",
                "data": ProductAttributeValueSerializer(
                    value
                ).data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # DELETE VALUE
    # ==========================================

    def delete(self, request, id):

        value = get_object_or_404(
            ProductAttributeValue,
            id=id
        )

        value.is_active = False

        value.save(
            update_fields=["is_active"]
        )

        return Response(
            {
                "success": True,
                "message": "Attribute value deleted successfully",
            },
            status=status.HTTP_200_OK
        )

class ProductVariantView(APIView):

    # ==========================================
    # CREATE VARIANT
    # ==========================================

    def post(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id,
            is_deleted=False
        )

        serializer = ProductVariantCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        attributes_data = validated_data.pop(
            "attribute_values",
            []
        )

        # ------------------------------------------
        # Validate attributes before creating variant
        # ------------------------------------------

        for attribute_data in attributes_data:

            attribute = attribute_data["attribute"]
            value = attribute_data["value"]

            # Attribute must belong to product category

            if attribute.category_id != product.category_id:

                return Response(
                    {
                        "success": False,
                        "message": (
                            f"Attribute '{attribute.name}' "
                            "does not belong to the "
                            "product category."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Value must belong to attribute

            if value.attribute_id != attribute.id:

                return Response(
                    {
                        "success": False,
                        "message": (
                            f"Value '{value.value}' "
                            f"does not belong to "
                            f"attribute '{attribute.name}'."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ------------------------------------------
        # Generate SKU
        # ------------------------------------------

        sku = ProductService.generate_variant_sku(
            product=product,
            attributes_data=attributes_data
        )

        # ------------------------------------------
        # Create variant
        # ------------------------------------------

        variant = ProductVariant.objects.create(
            product=product,
            sku=sku,
            **validated_data
        )

        # ------------------------------------------
        # Create variant attributes
        # ------------------------------------------

        for attribute_data in attributes_data:

            VariantAttributeValue.objects.create(
                variant=variant,
                **attribute_data
            )

        return Response(
            {
                "success": True,
                "message": "Product variant created successfully",
                "data": ProductVariantCreateSerializer(
                    variant
                ).data,
            },
            status=status.HTTP_201_CREATED
        )

    # ==========================================
    # LIST VARIANTS
    # ==========================================

    def get(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id,
            is_deleted=False
        )

        variants = ProductVariant.objects.filter(
            product=product,
            is_deleted=False
        ).prefetch_related(
            "attribute_values__attribute",
            "attribute_values__value"
        ).order_by(
            "-created_at"
        )

        serializer = ProductVariantCreateSerializer(
            variants,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": variants.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

class ProductVariantDetailView(APIView):
    # ==========================================
    # GET
    # ==========================================

    def get(self, request, id):

        variant = get_object_or_404(
            ProductVariant,
            id=id,
            is_deleted=False
        )

        serializer = ProductVariantCreateSerializer(
            variant
        )

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # PATCH
    # ==========================================

    def patch(self, request, id):

        variant = get_object_or_404(
            ProductVariant,
            id=id,
            is_deleted=False
        )

        serializer = ProductVariantCreateSerializer(
            variant,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        attributes_data = validated_data.pop(
            "attribute_values",
            None
        )

        # Update variant fields

        for field, value in validated_data.items():

            setattr(
                variant,
                field,
                value
            )

        variant.save()

        # Update attributes if supplied

        if attributes_data is not None:

            # Remove old attributes

            variant.attribute_values.all().delete()

            for attribute_data in attributes_data:

                attribute = attribute_data["attribute"]
                value = attribute_data["value"]

                # Check category

                if (
                    attribute.category_id
                    != variant.product.category_id
                ):

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"Attribute "
                                f"'{attribute.name}' "
                                "does not belong to "
                                "product category."
                            ),
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check value

                if value.attribute_id != attribute.id:

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"Value '{value.value}' "
                                "does not belong to "
                                f"attribute '{attribute.name}'."
                            ),
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                VariantAttributeValue.objects.create(
                    variant=variant,
                    attribute=attribute,
                    value=value
                )

        return Response(
            {
                "success": True,
                "message": "Product variant updated successfully",
                "data": ProductVariantCreateSerializer(
                    variant
                ).data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # DELETE
    # ==========================================

    def delete(self, request, id):

        variant = get_object_or_404(
            ProductVariant,
            id=id,
            is_deleted=False
        )

        variant.is_deleted = True
        variant.is_active = False

        variant.save(
            update_fields=[
                "is_deleted",
                "is_active"
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Product variant deleted successfully",
            },
            status=status.HTTP_200_OK
        )