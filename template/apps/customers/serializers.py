from rest_framework import serializers
from apps.customers.models import CustomerProfile
from  utils.googledrive.google_cloud import upload_file_to_drive

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
                folder_name=f"employee_{user.id}",
            )

        customer = CustomerProfile.objects.create(
            user=user,
            profile_image=image_data,
            **validated_data
        )

        return customer