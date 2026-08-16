from rest_framework import serializers
from apps.brands.models import Brand
from django.db import transaction
from  utils.googledrive.google_cloud import upload_file_to_drive,delete_file_from_drive


class BrandSerializer(serializers.ModelSerializer):
    brand_image=serializers.ImageField(required=False,allow_null=True,write_only=True)
    image=serializers.JSONField(read_only=True)
    class Meta:
        model=Brand
        fields="__all__"
        read_only_fields=["id","slug","image","is_deleted","created_at",
            "updated_at"]

    @transaction.atomic
    def create(self, validated_data):
        brand_image=validated_data.pop("brand_image",None)

        brand=Brand.objects.create(**validated_data)
        if brand_image:
            brand_image=upload_file_to_drive(
                file=brand_image,
                entity_type="Brand",
                folder_name=brand.name
            )
            brand.image=brand_image
            brand.save(update_fields=["image"])

        return brand

    @transaction.atomic
    def update(self, instance, validated_data):
        new_image=validated_data.pop("brand_name",None)

        for field,value in validated_data.items():
            setattr(instance,field,value)

        instance.save()

        if new_image:
            old_image=instance.image
            old_file_id=None

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
                    entity_type="Brand",
                    folder_name=instance.name,
                        )
            
            instance.image = image_data        
            instance.save(update_fields=[
                                "image",
                            ])
            
            return instance        