from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from apps.categories.serializers import CategorySerializer
from rest_framework.response import Response
from rest_framework import status
from apps.categories.models import Category

# Create your views here.
class CategoryView(APIView):

    def post(self, request):

        serializer = CategorySerializer(
            data=request.data)

        serializer.is_valid(
            raise_exception=True
        )

        category = serializer.save()

        return Response(
            {"success": True,
                "message": "Category created successfully.",
                "data": CategorySerializer(category).data,},status=status.HTTP_201_CREATED,
        )

    def get(self, request, id=None):

        if id:

            category = get_object_or_404(
                Category,
                id=id,
                is_deleted=False,
            )

            serializer = CategorySerializer(
                category
            )

            return Response(
                {
                    "success": True,
                    "message": "Category retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        categories = Category.objects.filter(
            is_deleted=False
        ).order_by("name")

        serializer = CategorySerializer(
            categories,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Categories retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, id):

        category = get_object_or_404(
            Category,
            id=id,
            is_deleted=False,
        )

        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Category updated successfully.",
                "data": CategorySerializer(category).data,
            },status=status.HTTP_200_OK,
        )

    def delete(self, request, id):

        category = get_object_or_404(
            Category,
            id=id,
            is_deleted=False,
        )

        category.is_deleted = True
        category.is_active = False

        category.save(
            update_fields=[
                "is_deleted",
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Category deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )