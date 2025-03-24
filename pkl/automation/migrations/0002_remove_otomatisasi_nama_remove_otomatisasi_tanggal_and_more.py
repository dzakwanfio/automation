# Generated by Django 5.1.7 on 2025-03-24 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otomatisasi',
            name='nama',
        ),
        migrations.RemoveField(
            model_name='otomatisasi',
            name='tanggal',
        ),
        migrations.AddField(
            model_name='otomatisasi',
            name='course_model',
            field=models.CharField(default='General', max_length=255),
        ),
        migrations.AddField(
            model_name='otomatisasi',
            name='course_name',
            field=models.CharField(default='Unknown Course', max_length=255),
        ),
        migrations.AddField(
            model_name='otomatisasi',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='otomatisasi',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.AddField(
            model_name='otomatisasi',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
