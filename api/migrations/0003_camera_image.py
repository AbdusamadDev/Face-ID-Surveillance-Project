# Generated by Django 4.2.5 on 2023-10-17 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_criminals"),
    ]

    operations = [
        migrations.AddField(
            model_name="camera",
            name="image",
            field=models.ImageField(default=1, upload_to="camera_images/"),
            preserve_default=False,
        ),
    ]