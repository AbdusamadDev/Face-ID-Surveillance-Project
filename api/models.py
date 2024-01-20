from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import FileSystemStorage


def criminal_image_path(instance, filename):
    return f"criminals/{instance.pk}/main.jpg"


class Camera(models.Model):
    name = models.CharField(max_length=150, null=False, unique=False, blank=False)
    image = models.ImageField(
        upload_to="./cameras/", default="none", null=False, blank=False
    )
    url = models.CharField(max_length=150, unique=False, null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False, unique=False)
    latitude = models.FloatField(null=False, blank=False, unique=False)


class Criminals(models.Model):
    first_name = models.CharField(max_length=120, null=False, blank=False, unique=False)
    middle_name = models.CharField(
        max_length=120, null=False, blank=False, unique=False, default="sss"
    )
    last_name = models.CharField(max_length=120, null=False, unique=False, blank=False)
    age = models.IntegerField(blank=False, null=False, unique=False)
    description = models.TextField(
        max_length=5000, blank=False, null=False, unique=False
    )
    image = models.ImageField(upload_to=criminal_image_path)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["first_name", "last_name", "age"])]

    def save(self, *args, **kwargs):
        temp_image = self.image
        self.image = None
        super().save(*args, **kwargs)
        self.image = temp_image
        if "force_insert" in kwargs:
            kwargs.pop("force_insert")
        super().save(*args, **kwargs)
        if self.image:
            storage = FileSystemStorage()
            new_path = criminal_image_path(self, self.image.name)
            if not storage.exists(new_path):
                old_path = self.image.name
                self.image.save(new_path, storage.open(old_path))
                storage.delete(old_path)


class CriminalsRecords(models.Model):
    criminal = models.ForeignKey(to=Criminals, on_delete=models.CASCADE, default=1)
    camera = models.ForeignKey(to=Camera, on_delete=models.CASCADE, default=1)
    image_path = models.URLField(default="https://www.image-test.com")
    date_recorded = models.DateTimeField(auto_now_add=True)


class TempRecords(models.Model):
    criminal = models.ForeignKey(to=Criminals, on_delete=models.CASCADE, default=1)
    camera = models.ForeignKey(to=Camera, on_delete=models.CASCADE, default=1)
    image_path = models.URLField(default="https://www.image-test.com")
    date_recorded = models.DateTimeField(auto_now_add=True)


class TempClientLocations(models.Model):
    longitude = models.FloatField(unique=True)
    latitude = models.FloatField(unique=True)


class UniqueKey(models.Model):
    uuid = models.UUIDField()


class WebTempRecords(models.Model):
    camera = models.ForeignKey(to=Camera, on_delete=models.CASCADE)
    criminal = models.ForeignKey(to=Criminals, on_delete=models.CASCADE)
    image_path = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
