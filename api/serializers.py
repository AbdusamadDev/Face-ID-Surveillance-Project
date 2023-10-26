from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from rest_framework import serializers

from api.models import Camera, Criminals, Encodings
from api.utils import host_address, process_image, is_allowed_chr, is_already_in

import os
import cv2
import numpy as np


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"

    def validate_name(self, value):
        exception = ValidationError(
            f"Field name: Only letters, capital letters, digits, and underscore are allowed."
        )
        if value:
            is_allowed_chr(value, exception=exception)
        return value


class CriminalsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Criminals
        fields = "__all__"

    def validate(self, attrs):
        exception = ValidationError(
            "Name fields: Only letters, capital letters, digits, and underscore are allowed."
        )
        if attrs.get("first_name"):
            is_allowed_chr(attrs.get("first_name"), exception)
        if attrs.get("last_name"):
            is_allowed_chr(attrs.get("last_name"), exception)

        image = attrs.get("image")
        if image:
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)

            if encoding is None:
                raise ValidationError({"msg": "No face found in entered image!"})
            elif len(encoding) != 1:
                raise ValidationError({"msg": "Only one face is allowed in one image!"})

        return attrs

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        instance = super(CriminalsSerializer, self).create(validated_data)
        print("Creation is being creation")
        if image:
            print("Image exists")
            file_storage = FileSystemStorage()
            path = os.path.join("criminals", str(instance.pk), "main.jpg")
            file_storage.save(path, image)
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)
            new_encoding = list(encoding[0].embedding)
            Encodings.objects.create(criminal=instance, encoding=new_encoding)

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image_url"] = f"{host_address}/media/criminals/{instance.pk}/main.jpg"
        return rep

    def update(self, instance, validated_data):
        image = self.context["request"].FILES.get("image")

        if image is not None:
            img_path = os.path.join("criminals", str(instance.pk), "main.jpg")
            if default_storage.exists(img_path):
                default_storage.delete(img_path)
            default_storage.save(img_path, image)
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)
            new_encoding = encoding[0].embedding

            if encoding is not None:
                new_encoding = encoding[0].embedding.tolist()
                try:
                    encoding_obj = Encodings.objects.get(criminal=instance.pk)
                    encoding_obj.encoding = new_encoding
                    encoding_obj.save()
                except Encodings.DoesNotExist:
                    print(f"Encoding Object does not exist for pk: {instance.pk}")

        return super().update(instance, validated_data)
