# Generated by Django 4.2.5 on 2023-11-03 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_camera_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='camera',
            name='longitude',
            field=models.FloatField(),
        ),
    ]
