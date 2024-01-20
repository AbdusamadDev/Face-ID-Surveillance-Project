# Generated by Django 5.0.1 on 2024-01-20 08:46

import api.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('image', models.ImageField(default='none', upload_to='./cameras/')),
                ('url', models.CharField(max_length=150)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TempClientLocations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('longitude', models.FloatField(unique=True)),
                ('latitude', models.FloatField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField()),
            ],
        ),
        migrations.CreateModel(
            name='Criminals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=120)),
                ('middle_name', models.CharField(default='sss', max_length=120)),
                ('last_name', models.CharField(max_length=120)),
                ('age', models.IntegerField()),
                ('description', models.TextField(max_length=5000)),
                ('image', models.ImageField(upload_to=api.models.criminal_image_path)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'indexes': [models.Index(fields=['first_name', 'last_name', 'age'], name='api_crimina_first_n_d983bc_idx')],
            },
        ),
        migrations.CreateModel(
            name='CriminalsRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_path', models.URLField(default='https://www.image-test.com')),
                ('date_recorded', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.camera')),
                ('criminal', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.criminals')),
            ],
        ),
        migrations.CreateModel(
            name='TempRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_path', models.URLField(default='https://www.image-test.com')),
                ('date_recorded', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.camera')),
                ('criminal', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.criminals')),
            ],
        ),
        migrations.CreateModel(
            name='WebTempRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.camera')),
                ('criminal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.criminals')),
            ],
        ),
    ]
