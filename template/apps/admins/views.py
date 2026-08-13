from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    AdminLoginSerializer,
    AdminOTPVerifySerializer,
)

from .services.admin_auth_service import AdminAuthService

class AdminLoginAPIView(APIView):

    def post(self, request):

        serializer = AdminLoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            user = AdminAuthService.login(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

        except ValidationError as e:

            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "OTP sent to admin email.",
                "data": {
                    "email": user.email,
                    "otp_required": True,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminOTPVerifyAPIView(APIView):

    def post(self, request):

        serializer = AdminOTPVerifySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            result = AdminAuthService.verify_otp(
                email=serializer.validated_data["email"],
                otp=serializer.validated_data["otp"],
            )

        except ValidationError as e:

            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = result["user"]

        return Response(
            {
                "success": True,
                "message": "Admin login successful.",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                    "tokens": {
                        "refresh": result["refresh"],
                        "access": result["access"],
                    },
                },
            },
            status=status.HTTP_200_OK,
        )