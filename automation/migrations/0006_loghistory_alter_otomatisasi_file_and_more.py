# Generated by Django 5.1.7 on 2025-04-14 03:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0005_alter_otomatisasi_file_alter_uploadedfile_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('course_name', models.CharField(max_length=255)),
                ('status', models.CharField(default='Success', max_length=20)),
                ('process_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AlterField(
            model_name='otomatisasi',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]
