from rest_framework import serializers
from apps.categories.models import Category

from utils.googledrive.google_cloud import (
    upload_file_to_drive,
    delete_file_from_drive,
)

from django.db.transaction import atomic


class CategorySerializer(serializers.ModelSerializer):

    category_image = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    image = serializers.JSONField(
        read_only=True
    )

    class Meta:
        model = Category

        fields = "__all__"

        read_only_fields = [
            "id",
            "slug",
            "image",
            "created_at",
            "updated_at",
        ]

    @atomic
    def create(self, validated_data):

        # Get uploaded image
        category_image = validated_data.pop(
            "category_image",
            None
        )

        # Create category first
        category = Category.objects.create(
            **validated_data
        )

        # Upload image to Google Drive
        if category_image:

            image_data = upload_file_to_drive(
                file=category_image,
                entity_type="Categories",
                folder_name=category.name,
            )

            category.image = image_data

            category.save(
                update_fields=[
                    "image",
                    "updated_at",
                ]
            )

        return category

    @atomic
    def update(self, instance, validated_data):

        new_image = validated_data.pop(
            "category_image",
            None
        )

        # Update category fields
        for field, value in validated_data.items():
            setattr(
                instance,
                field,value)

        instance.save()

        # Replace image
        if new_image:

            old_image = instance.image

            old_file_id = None

            if old_image:
                old_file_id = old_image.get(
                    "file_id"
                )

            if old_file_id:
                delete_file_from_drive(
                    old_file_id
                )

            image_data = upload_file_to_drive(
                file=new_image,
                entity_type="Categories",
                folder_name=instance.name,
            )

            instance.image = image_data

            instance.save(
                update_fields=[
                    "image",
                    "updated_at",
                ]
            )

        return instance