from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.vendors.models import VendorProfile
from apps.vendors.serializers import VendorSerializer,EmailVerifySerializer
from apps.accounts.models import User
from django.utils import timezone


class VendorAPIView(APIView):

    def post(self,request):
        serializer = VendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Vendor created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self,request,id=None):
        if id:
            vendor=get_object_or_404(VendorProfile.objects.select_related(
                    "user"),id=id,is_deleted=False)
            serializer=VendorSerializer(vendor)
            return Response(serializer.data,status=status.HTTP_200_OK)
        activestatus=request.query_params.get("active_status",False)
        vendor=VendorProfile.objects.select_related("user").filter(is_deleted=activestatus).order_by("created_at")
        serializer=VendorSerializer(vendor,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def patch(self,request,id):
        vendor=get_object_or_404(VendorProfile,id=id)
        serializer=VendorSerializer(vendor,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VendorApprovalView(APIView):

    def patch(self, request):

        ids = request.data.get("ids", [])
        approval_status = request.data.get("status")

        if not ids:
            return Response(
                {
                    "success": False,
                    "message": "Vendor IDs are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_statuses = [
            VendorProfile.ApprovalStatus.APPROVED,
            VendorProfile.ApprovalStatus.REJECTED,
        ]

        if approval_status not in allowed_statuses:
            return Response(
                {
                    "success": False,
                    "message": "Invalid approval status."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        vendors = VendorProfile.objects.filter(
            id__in=ids,
            is_deleted=False,
        )

        if not vendors.exists():
            return Response(
                {
                    "success": False,
                    "message": "No vendors found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        update_data = {
            "approval_status": approval_status,
        }

        if approval_status == VendorProfile.ApprovalStatus.APPROVED:
            update_data["approved_at"] = timezone.now()

        elif approval_status == VendorProfile.ApprovalStatus.REJECTED:
            update_data["approved_at"] = None

        updated_count = vendors.update(
            **update_data
        )

        return Response(
            {
                "success": True,
                "message": (
                    f"{updated_count} vendor(s) "
                    f"{approval_status.lower()} successfully."
                ),
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )