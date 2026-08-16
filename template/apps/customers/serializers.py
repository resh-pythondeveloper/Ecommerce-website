from rest_framework import serializers
from apps.customers.models import CustomerProfile
from  utils.googledrive.google_cloud import upload_file_to_drive,delete_file_from_drive

class CustomerSerializer(serializers.ModelSerializer):
    profile_image = serializers.JSONField(
        read_only=True
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True,
    )
    class Meta:
        model=CustomerProfile
        fields="__all__"
        read_only_fields =["user","id","profile_image","created_at","updated_at"]

    def create(self, validated_data):

        profile_image = validated_data.pop(
            "image",
            None
        )

        user = self.context["request"].user

        image_data = None

        if profile_image:

            image_data = upload_file_to_drive(
                file=profile_image,
                entity_type="Customers",
                folder_name=f"{user.username}_{user.id}",
            )

        customer = CustomerProfile.objects.create(
            user=user,
            profile_image=image_data,
            **validated_data
        )

        return customer
    
    def update(self, instance, validated_data):

        # Get new uploaded image
        new_image = validated_data.pop(
            "image",
            None
        )

        # Update normal profile fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # Update profile image only if a new image is provided
        if new_image:

            # Get old image information
            old_image = instance.profile_image

            old_file_id = None

            if old_image:
                old_file_id = old_image.get("file_id")

            # Delete old Google Drive image
            if old_file_id:

                delete_file_from_drive(
                    old_file_id
                )

            # Upload new image
            user = instance.user

            image_data = upload_file_to_drive(
                file=new_image,
                entity_type="Customers",
                folder_name=f"{user.username}_{user.id}",
            )

            # Save new Google Drive metadata
            instance.profile_image = image_data

            instance.save(
                update_fields=[
                    "profile_image",
                    "updated_at",
                ]
            )

        return instance