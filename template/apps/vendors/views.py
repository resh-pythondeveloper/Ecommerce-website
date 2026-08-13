from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.vendors.models import VendorProfile
from apps.vendors.serializers import VendorSerializer,EmailVerifySerializer
from apps.accounts.models import User
from apps.accounts.services.otp_service import OTPService
from django.core.exceptions import ValidationError

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


class VendorEmailVerifyView(APIView):

    def post(self, request):

        serializer = EmailVerifySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        user = User.objects.filter(
            email=email,
            role=User.Role.VENDOR,
            is_deleted=False).first()

        if not user:
            return Response(
                {
                    "success": False,
                    "message": "Vendor not found.",
                },status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_email_verified:
            return Response(
                {
                    "success": False,
                    "message": "Email is already verified.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            OTPService.verify_otp(
                user=user,otp=otp)

        except ValidationError as e:

            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_email_verified = True

        user.save(
            update_fields=[
                "is_email_verified",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Email verified successfully. "
                    "Your vendor account is pending approval."
                ),
            },
            status=status.HTTP_200_OK,)