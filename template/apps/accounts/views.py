from django.shortcuts import render
from rest_framework.views import APIView
from apps.accounts.serializers import RegisterSerializer,VerifyEmailSerializer,LoginSerializer
from rest_framework import status
from rest_framework.response import Response
from apps.accounts.services.auth_service import AuthService
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.accounts.services.otp_service import OTPService
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=AuthService.register_customer(**serializer.validated_data)
            return Response(
            {
                "success": True,
                "message": (
                    "Registration started. "
                    "Email OTP sent."
                ),
                "data": {
                    "user_id": user.id,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyEmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:

            user = User.objects.get(
                email=email,
                is_deleted=False,
            )

            mobile_otp = AuthService.verify_email(
                user=user,
                otp=otp,
            )

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except ValidationError as error:

            return Response(
                {
                    "success": False,
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": (
                    "Email verified. "
                    "Mobile OTP sent."
                ),

                # Development only
                "mobile_otp": mobile_otp,
            },
            status=status.HTTP_200_OK,
        )

class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyEmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:

            user = User.objects.get(
                email=email,
                is_deleted=False,
            )

            AuthService.verify_email(
                user=user,
                otp=otp)

        except User.DoesNotExist:
            return Response(
                {"success": False,
                    "message": "User not found."},status=status.HTTP_404_NOT_FOUND)

        except ValidationError as error:

            return Response(
                {
                    "success": False,
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": (
                    "Email verified. "
                )},status=status.HTTP_200_OK,
        )


class ResendOTPView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        email=request.data.get("email")
        user=User.objects.filter(email=email,is_deleted=False).first()

        if not user:
            return Response({"success": False, "message": "User not found."},status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({"success": False, "message": "Email already verified."},status=status.HTTP_400_BAD_REQUEST)
        
        OTPService.resend_otp(user=user)

        return Response({"success": True, "message": "OTP resent successfully."},status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):

        serializer=LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        try:
            user=AuthService.login_user(**serializer.validated_data)
            tokens=AuthService.generate_tokens(user=user)

            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "mobile_number": user.mobile_number,
                            "role": user.role,
                        },
                        "tokens": tokens,
                    }},status=status.HTTP_200_OK,
            )
        except ValidationError as e:

            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class RefreshTokenAPIView(TokenRefreshView):
    pass

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."},status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },status=status.HTTP_400_BAD_REQUEST)