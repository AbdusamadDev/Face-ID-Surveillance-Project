from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.utils import host_address, process_image
from api.models import (
    CriminalsRecords,
    Criminals,
    Encodings,
    Camera,
)

import numpy as np
import cv2
import os


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CameraSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.method == 'PATCH':
            self.fields['image'].required = False
            self.fields['image'].allow_null = True

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        instance = Camera.objects.create(**validated_data)

        if image:
            instance.image.save(image.name, image)
            instance.save()

        return instance

    def validate_image(self, value):
        if value is not None and not hasattr(value, 'file'):
            raise serializers.ValidationError("This field should be a file.")
        return value

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)

        if image is not None:
            instance.image.delete(save=False)  # Delete old image file.

            # Save the new image
            instance.image.save(image.name, image, save=False)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CriminalsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = Criminals
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CriminalsSerializer, self).__init__(*args, **kwargs)

        # Make all fields not required if the request method is PATCH
        if self.context.get('request', None) and self.context['request'].method == 'PATCH':
            for field_name, field in self.fields.items():
                field.required = False
                print(field)

    def validate(self, attrs):
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
        if image:
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
        if image is None:
            image = validated_data.get("image")
        if image is not None:
            img_path = os.path.join("criminals", str(instance.pk), "main.jpg")
            if default_storage.exists(img_path):
                default_storage.delete(img_path)
            default_storage.save(img_path, image)
            image.seek(0)
            nparr = np.frombuffer(image.read(), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            encoding = process_image(img_np)

            if encoding is not None:
                new_encoding = encoding[0].embedding.tolist()
                try:
                    encoding_obj = Encodings.objects.get(criminal=instance.pk)
                    encoding_obj.encoding = new_encoding
                    encoding_obj.save()
                except Encodings.DoesNotExist:
                    print(f"Encoding Object does not exist for pk: {instance.pk}")

        return super().update(instance, validated_data)


class CriminalsRecordsSerializer(serializers.ModelSerializer):
    criminal = CriminalsSerializer(read_only=True)
    camera = CameraSerializer(read_only=True)
    class Meta:
        fields = "__all__"
        model = CriminalsRecords
