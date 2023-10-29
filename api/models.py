from django.db import models
from django.contrib.postgres.fields import ArrayField


class Camera(models.Model):
    name = models.CharField(max_length=150, null=False, unique=True, blank=False)
    image = models.ImageField(upload_to="./cameras/", default="none", null=False, blank=False)
    url = models.CharField(max_length=150, unique=True, null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False, unique=True)
    latitude = models.FloatField(null=False, blank=False, unique=True)


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
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["first_name", "last_name", "age"])]

class Encodings(models.Model):
    criminal = models.ForeignKey(to=Criminals, on_delete=models.CASCADE)
    encoding = ArrayField(models.FloatField())
