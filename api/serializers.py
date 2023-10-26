from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from api.models import Camera, Criminals, Encodings
from api.utils import (
    allowed_characters,
    host_address,
    process_image,
    is_already_in,
    is_allowed_chr,
)

import shutil
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request.method == "PUT":
            for field in self.fields.values():
                field.required = True
        elif request.method == "PATCH":
            for field in self.fields.values():
                field.required = False

    def validate(self, attrs):
        exception = ValidationError(
            f"Name fields: Only letters, capital letters, digits, and underscore are allowed."
        )
        if attrs.get("first_name"):
            is_allowed_chr(attrs.get("first_name"), exception)
        if attrs.get("last_name"):
            is_allowed_chr(attrs.get("last_name"), exception)
        first_name = attrs.get("first_name")
        image = attrs.get("image")
        if image:
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)
            # Image validation goes here
            if encoding is None:
                raise ValidationError(
                    {"msg": "No face found in entered image!"},
                )
            elif len(encoding) != 1:
                raise ValidationError(
                    {"msg": "Only one face is allowed in one image!"},
                )
            else:
                new_encoding = encoding[0].embedding
                name = is_already_in(new_encoding)
                if name is not None:
                    if name != first_name:
                        raise ValidationError(
                            {
                                "msg": f"Criminal in image with name of {name} is already in database!"
                            },
                        )
                else:
                    new_encoding = list(new_encoding)
            try:
                request_method = self.context["request"].method
                print(request_method)
                if request_method == "POST":
                    Encodings.objects.create(criminal=first_name, encoding=new_encoding)
            except Exception:
                raise ValidationError(
                    "Something went wrong with image encoding, please try again"
                )
        return attrs

    def create(self, validated_data):
        image = validated_data.pop("image", None)

        if image:
            file_storage = FileSystemStorage()
            path = os.path.join(
                "media", "criminals", validated_data["first_name"], "main.jpg"
            )

            file_storage.save(path, image)

        instance = super(CriminalsSerializer, self).create(validated_data)
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        username = instance.first_name
        rep["image_url"] = f"{host_address}/media/criminals/{username}/main.jpg"

        return rep

    def save_image(self, instance, image):
        dir_path = os.path.join("criminals", instance.first_name)
        if os.path.exists(dir_path):
            os.mkdir(dir_path)
        file_storage = FileSystemStorage()
        file_storage.save(os.path.join(dir_path, "main.jpg"), image)

    def save(self, *args, **kwargs):
        image = self.validated_data.pop("image", None)
        instance = super().save(*args, **kwargs)
        if image:
            self.save_image(instance, image)
        return instance

    def update(self, instance, validated_data):
        image = self.context["request"].FILES.get("image")
        first_name = validated_data.get("first_name", None)

        if first_name:
            old_path = os.path.join("media", "criminals", instance.first_name)
            new_path = os.path.join("media", "criminals", first_name)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
            instance.first_name = first_name
            try:
                try:
                    update_first_name = self.Meta.model.objects.get(pk=instance.pk)
                except:
                    print(f"Object with pk: {instance.pk} does not exist")
                encoding_obj = Encodings.objects.get(
                    criminal=update_first_name.first_name
                )
                encoding_obj.criminal = first_name
                encoding_obj.save()
            except Encodings.DoesNotExist:
                print("Object does not exist!")
        if image is not None:
            if first_name:
                img_path = os.path.join("media", "criminals", first_name, "main.jpg")
            else:
                img_path = os.path.join(
                    "media", "criminals", instance.first_name, "main.jpg"
                )

            if os.path.exists(img_path):
                os.remove(img_path)
            else:
                print(first_name)
                print("Image does not exist!")
            file_storage = FileSystemStorage()
            file_storage.save(img_path, image)
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)
            new_encoding = encoding[0].embedding
            if encoding is not None:
                new_encoding = encoding[0].embedding.tolist()
                try:
                    encoding_obj = Encodings.objects.get(criminal=instance.first_name)
                    encoding_obj.encoding = new_encoding
                    encoding_obj.save()
                except Encodings.DoesNotExist:
                    print("Encoding Object does not exist!")

        return super().update(instance=instance, validated_data=validated_data)
