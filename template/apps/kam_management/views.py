from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.kam_management.serializers import KAMSerializer
from apps.kam_management.models import KAM
class KAMCreateAPIView(APIView):

    def post(self, request):
        serializer = KAMSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "KAM created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self,request,id=None):
        if id:
            try:
                kam = KAM.objects.get(id=id)
            except KAM.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "KAM not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = KAMSerializer(kam)
            return Response(
                {
                    "success": True,
                    "message": "KAM retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        active_status = request.query_params.get("active_status", False)
        kam=KAM.objects.select_related("user").filter(is_deleted=active_status).order_by("created_at")
        serializer = KAMSerializer(kam,many=True)
        return Response(
            {
                "success": True,
                "message": "KAM retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK)

    def patch(self,request,id):
        try:
            kam = KAM.objects.get(id=id)
        except KAM.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "KAM not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = KAMSerializer(
            kam,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "KAM updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )