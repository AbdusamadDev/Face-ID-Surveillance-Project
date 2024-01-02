# Generated by Django 5.0 on 2023-12-25 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_delete_encodings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criminalsrecords',
            name='image_path',
            field=models.URLField(default='https://www.image-test.com'),
        ),
        migrations.CreateModel(
            name='TempRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.criminalsrecords')),
            ],
        ),
    ]
