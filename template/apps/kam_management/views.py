from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.kam_management.serializers import KAMSerializer
from apps.kam_management.models import KAM
from apps.vendors.models import VendorProfile
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

class AssignKAMToVendor(APIView):

    def patch(self, request, kam_id):

        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {
                    "success": False,
                    "message": "Vendor IDs are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        kam = get_object_or_404(
            KAM,
            id=kam_id,
            is_active=True,
            is_deleted=False,
        )

        vendors = VendorProfile.objects.filter(
            id__in=ids,
            approval_status=VendorProfile.ApprovalStatus.APPROVED,
            is_deleted=False,
        )

        if not vendors.exists():
            return Response(
                {
                    "success": False,
                    "message": "No approved vendors found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        updated_count = vendors.update(
            kam=kam
        )

        return Response(
            {
                "success": True,
                "message": "KAM assigned successfully.",
                "updated_count": updated_count,
                "kam_id": kam.kam_id,
            },
            status=status.HTTP_200_OK,
        )