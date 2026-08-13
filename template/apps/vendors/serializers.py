from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import User
from apps.vendors.models import VendorProfile
from apps.accounts.services.otp_service import OTPService

from utils.googledrive.google_cloud import (
    upload_file_to_drive,
    delete_file_from_drive,
)


class VendorSerializer(serializers.ModelSerializer):

    # ==========================================
    # USER INPUT FIELDS
    # ==========================================

    username = serializers.CharField(
        write_only=True
    )

    email = serializers.EmailField(
        write_only=True
    )

    mobile_number = serializers.CharField(
        write_only=True
    )

    password = serializers.CharField(
        write_only=True,
        required=False
    )

    # ==========================================
    # FILE INPUT FIELDS
    # ==========================================

    profile_image = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True
    )

    logo_image = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True
    )

    # ==========================================
    # STORED GOOGLE DRIVE DATA
    # ==========================================

    profile_picture = serializers.JSONField(
        read_only=True
    )

    logo = serializers.JSONField(
        read_only=True
    )

    class Meta:
        model = VendorProfile

        fields = "__all__"

        read_only_fields = [
            "id",
            "user",
            "vendor_id",
            "profile_picture",
            "logo",
            "approval_status",
            "approved_at",
            "kam",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

    # ==========================================
    # EMAIL VALIDATION
    # ==========================================

    def validate_email(self, value):

        queryset = User.objects.filter(
            email=value,
            is_deleted=False
        )

        if self.instance:
            queryset = queryset.exclude(
                id=self.instance.user.id
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value.lower()

    # ==========================================
    # USERNAME VALIDATION
    # ==========================================

    def validate_username(self, value):

        queryset = User.objects.filter(
            username=value,
            is_deleted=False
        )

        if self.instance:
            queryset = queryset.exclude(
                id=self.instance.user.id
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    # ==========================================
    # MOBILE VALIDATION
    # ==========================================

    def validate_mobile_number(self, value):

        queryset = User.objects.filter(
            mobile_number=value,
            is_deleted=False
        )

        if self.instance:
            queryset = queryset.exclude(
                id=self.instance.user.id
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Mobile number already exists."
            )

        return value

    # ==========================================
    # CREATE
    # ==========================================

    @transaction.atomic
    def create(self, validated_data):

        # --------------------------------------
        # User fields
        # --------------------------------------

        username = validated_data.pop(
            "username"
        )

        email = validated_data.pop(
            "email"
        )

        mobile_number = validated_data.pop(
            "mobile_number"
        )

        password = validated_data.pop(
            "password"
        )

        # --------------------------------------
        # Uploaded files
        # --------------------------------------

        profile_image = validated_data.pop(
            "profile_image",
            None
        )

        logo_image = validated_data.pop(
            "logo_image",
            None
        )

        # Create User

        user = User.objects.create_user(
            username=username,
            email=email,
            mobile_number=mobile_number,
            password=password,
            role=User.Role.VENDOR,
            is_email_verified=False,
        )

        # Create VendorProfile

        vendor = VendorProfile.objects.create(
            user=user,
            approval_status=(
                VendorProfile.ApprovalStatus.PENDING
            ),
            **validated_data
        )

        # Upload profile image

        if profile_image:

            profile_data = upload_file_to_drive(
                file=profile_image,
                entity_type="Vendors",
                folder_name=(
                    f"{username}_{vendor.vendor_id}"
                )
            )

            vendor.profile_picture = profile_data

        # Upload logo

        if logo_image:

            logo_data = upload_file_to_drive(
                file=logo_image,
                entity_type="Vendors",
                folder_name=(
                    f"{username}_{vendor.vendor_id}"
                )
            )

            vendor.logo = logo_data

        # Save Drive metadata

        if profile_image or logo_image:

            vendor.save(
                update_fields=[
                    "profile_picture",
                    "logo",
                    "updated_at",
                ]
            )

        # --------------------------------------
        # Send email OTP
        # --------------------------------------

        OTPService.create_otp(
            user=user
        )

        return vendor

    # ==========================================
    # UPDATE
    # ==========================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data
    ):

        # --------------------------------------
        # User fields
        # --------------------------------------

        username = validated_data.pop(
            "username",
            None
        )

        email = validated_data.pop(
            "email",
            None
        )

        mobile_number = validated_data.pop(
            "mobile_number",
            None
        )

        password = validated_data.pop(
            "password",
            None
        )

        # --------------------------------------
        # New files
        # --------------------------------------

        new_profile_image = validated_data.pop(
            "profile_image",
            None
        )

        new_logo_image = validated_data.pop(
            "logo_image",
            None
        )

        # --------------------------------------
        # Update User
        # --------------------------------------

        user = instance.user

        if username is not None:
            user.username = username

        if email is not None:
            if user.email != email:
                user.email = email
                user.is_email_verified = False

        if mobile_number is not None:
            user.mobile_number = mobile_number

        if password:
            user.set_password(password)

        user.save()

        # --------------------------------------
        # Update VendorProfile
        # --------------------------------------

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value
            )

        instance.save()

        # --------------------------------------
        # Update profile image
        # --------------------------------------

        if new_profile_image:

            old_picture = instance.profile_picture

            old_file_id = None

            if old_picture:
                old_file_id = old_picture.get(
                    "file_id"
                )

            if old_file_id:
                delete_file_from_drive(
                    old_file_id
                )

            profile_data = upload_file_to_drive(
                file=new_profile_image,
                entity_type="Vendors",
                folder_name=(
                    f"{user.username}_"
                    f"{instance.vendor_id}"
                )
            )

            instance.profile_picture = profile_data

        # --------------------------------------
        # Update logo
        # --------------------------------------

        if new_logo_image:

            old_logo = instance.logo

            old_file_id = None

            if old_logo:
                old_file_id = old_logo.get(
                    "file_id"
                )

            if old_file_id:
                delete_file_from_drive(
                    old_file_id
                )

            logo_data = upload_file_to_drive(
                file=new_logo_image,
                entity_type="Vendors",
                folder_name=(
                    f"{user.username}_"
                    f"{instance.vendor_id}"
                )
            )

            instance.logo = logo_data

        # --------------------------------------
        # Save file changes
        # --------------------------------------

        if new_profile_image or new_logo_image:

            instance.save(
                update_fields=[
                    "profile_picture",
                    "logo",
                    "updated_at",
                ]
            )

        return instance

    # ==========================================
    # RESPONSE
    # ==========================================

    def to_representation(self, instance):

        data = super().to_representation(
            instance
        )

        data["username"] = instance.user.username
        data["email"] = instance.user.email
        data["mobile_number"] = (
            instance.user.mobile_number
        )

        return data

class EmailVerifySerializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)