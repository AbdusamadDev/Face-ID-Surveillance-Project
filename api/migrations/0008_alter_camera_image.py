# Generated by Django 4.2.5 on 2023-10-21 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0007_camera_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="camera",
            name="image",
            field=models.ImageField(
                default="none",
                upload_to="home/legion/lab/MarketPlaceSecurityApp/media/cameras/",
            ),
        ),
    ]