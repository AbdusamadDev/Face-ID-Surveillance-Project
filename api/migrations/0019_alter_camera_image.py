# Generated by Django 4.2.5 on 2023-11-03 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_camera_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='image',
            field=models.ImageField(default='none', upload_to='./media/cameras/'),
        ),
    ]
