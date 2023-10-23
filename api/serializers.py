from rest_framework import serializers, viewsets
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage

from api.models import Camera, Criminals
from api.utils import allowed_characters, host_address

import os


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"

    def validate_name(self, value):
        self.check_allowed_characters(value, "name")
        return value

    def check_allowed_characters(self, value, field_name):
        for letter in value:
            if letter not in allowed_characters:
                raise ValidationError(
                    f"Field {field_name}: Only letters, capital letters, digits, and underscore are allowed."
                )


class CriminalsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = Criminals
        fields = "__all__"

    def validate(self, attrs):
        self.check_allowed_characters(attrs.get("first_name"), "first_name")
        self.check_allowed_characters(attrs.get("last_name"), "last_name")
        return attrs

    def check_allowed_characters(self, value, field_name):
        for letter in value:
            if letter not in allowed_characters:
                raise serializers.ValidationError(
                    f"Field {field_name}: Only letters, capital letters, digits, and underscore are allowed."
                )

    def create(self, validated_data):
        image = validated_data.pop("image", None)

        if image:
            file_storage = FileSystemStorage()
            path = os.path.join("criminals", validated_data["first_name"], "main.jpg")

            file_storage.save(path, image)

        instance = super(CriminalsSerializer, self).create(validated_data)
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        username = instance.first_name  # Assuming the folder name is first_name
        rep["image_url"] = f"{host_address}/media/criminals/{username}/main.jpg"
        
        return rep
