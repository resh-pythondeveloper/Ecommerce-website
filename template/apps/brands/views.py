from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.brands.serializers import BrandSerializer
from apps.brands.models import Brand
# Create your views here.
class BrandView(APIView):
    def post(self,request):
        serializer=BrandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        brand=serializer.save()

        return Response(
            {"succes":True,"message":"brand created Successfully","data":BrandSerializer(brand).data},status=status.HTTP_201_CREATED
        )

    def get(self,request,id=None):
        if id:
            brand=get_object_or_404(Brand,id=id,is_deleted=False)
            serializer=BrandSerializer(brand)
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
        brand=Brand.objects.filter(is_deleted=False).order_by("created_at")
        serializer=BrandSerializer(brand,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)

    def patch(self,request,id=None):
        brand=get_object_or_404(Brand,id=id,is_deleted=False)
        serializer=BrandSerializer(brand,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        brand=serializer.save()
        return Response({"data":BrandSerializer(brand).data},status=status.HTTP_200_OK)

    def delete(self, request, id=None):

        brand = get_object_or_404(
            Brand,
            id=id,
            is_deleted=False
        )

        brand.is_deleted = True
        brand.save(
            update_fields=["is_deleted"]
        )

        return Response(
            {
                "success": True,
                "message": "Brand deleted successfully"
            },
            status=status.HTTP_200_OK
        )