from rest_framework import serializers
from apps.kam_management.models import KAM
from apps.accounts.models import User
from django.db import transaction
from utils.googledrive.google_cloud import upload_file_to_drive,delete_file_from_drive

class KAMSerializer(serializers.ModelSerializer):
    profile_picture = serializers.JSONField(read_only=True)
    image = serializers.ImageField(
            required=False,
            allow_null=True,
            write_only=True)
    username=serializers.CharField(write_only=True)
    email=serializers.EmailField(write_only=True)
    mobile_number=serializers.CharField(write_only=True)
    password=serializers.CharField(write_only=True)

    class Meta:
        model=KAM
        fields="__all__"
        read_only_fields =["id","user","kam_id","profile_picture","created_at","updated_at","is_active","is_deleted"]

    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["username"] = instance.user.username
        data["email"] = instance.user.email
        data["mobile_number"] = instance.user.mobile_number

        return data

    def validate_email(self, value):

        if User.objects.filter(
            email=value,
            is_deleted=False
        ).exists():

            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate_username(self, value):

        if User.objects.filter(
            username=value,
            is_deleted=False
        ).exists():

            raise serializers.ValidationError(
                "Username already exists."
            )

        return value
    
    def validate_mobile_number(self, value):
        if User.objects.filter(
            mobile_number=value,
            is_deleted=False
        ).exists():

            raise serializers.ValidationError(
                "Mobile number already exists."
            )

        return value
    
    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        mobile_number = validated_data.pop("mobile_number")
        password = validated_data.pop("password")

        profile_picture = validated_data.pop("image",None)

        user = User.objects.create_user(
            username=username,
            email=email,
            mobile_number=mobile_number,
            role=User.Role.KAM,
            password=password,
            is_email_verified=True
        )

        kam = KAM.objects.create(
            user=user,
            **validated_data
        )

        if profile_picture:
            image_data = upload_file_to_drive(
                            file=profile_picture,
                            entity_type="KAM",
                            folder_name=f"{username}_{kam.kam_id}")
            kam.profile_picture = image_data

            kam.save(
                update_fields=["profile_picture"])
        return kam
    
    @transaction.atomic
    def update(self, instance, validated_data):

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
            "password",None)

        # ----------------------------
        # New profile image
        # ----------------------------

        new_image = validated_data.pop(
            "image",
            None
        )

        # ----------------------------
        # Update User
        # ----------------------------

        user = instance.user

        if username is not None:
            user.username = username

        if email is not None:
            user.email = email

        if mobile_number is not None:
            user.mobile_number = mobile_number

        if password:
            user.set_password(password)

        user.save()

        # ----------------------------
        # Update KAM fields
        # ----------------------------

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        # ----------------------------
        # Update profile image
        # ----------------------------

        if new_image:

            old_image = instance.profile_picture

            old_file_id = None

            if old_image:

                old_file_id = old_image.get(
                    "file_id"
                )

            # Delete old image
            if old_file_id:

                delete_file_from_drive(
                    old_file_id
                )

            # Upload new image
            image_data = upload_file_to_drive(
                file=new_image,
                entity_type="KAM",
                folder_name=(
                    f"{user.username}_"
                    f"{instance.kam_id}"
                )
            )

            instance.profile_picture = image_data

            instance.save(
                update_fields=[
                    "profile_picture"
                ]
            )

        return instance