from rest_framework import serializers

from api.utils import host_address
from api.models import (
    TempClientLocations,
    CriminalsRecords,
    WebTempRecords,
    TempRecords,
    Criminals,
    Camera,
)


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CameraSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.method == "PATCH":
            self.fields["image"].required = False
            self.fields["image"].allow_null = True

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        instance = Camera.objects.create(**validated_data)

        if image:
            instance.image.save(image.name, image)
            instance.save()

        return instance

    def validate_image(self, value):
        if value is not None and not hasattr(value, "file"):
            raise serializers.ValidationError("This field should be a file.")
        return value

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)

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
        if (
            self.context.get("request", None)
            and self.context["request"].method == "PATCH"
        ):
            for field_name, field in self.fields.items():
                field.required = False
                print(field)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image_url"] = f"{host_address}/media/criminals/{instance.pk}/main.jpg"
        return rep


class CriminalsRecordsSerializer(serializers.ModelSerializer):
    criminal = CriminalsSerializer(read_only=True)
    camera = CameraSerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = CriminalsRecords


class TempRecordsSerializer(serializers.ModelSerializer):
    record = CriminalsRecordsSerializer()

    class Meta:
        fields = "__all__"
        model = TempRecords


class TempClientLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = TempClientLocations


class WebTempRecordsSerializer(serializers.ModelSerializer):
    criminal = CriminalsSerializer()
    camera = CameraSerializer() 
    class Meta:
        fields = "__all__"
        model = WebTempRecords