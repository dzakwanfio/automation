# Generated by Django 5.1.7 on 2025-05-23 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0018_peserta_is_converted'),
    ]

    operations = [
        migrations.AddField(
            model_name='loghistory2',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='loghistory2',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='loghistory2',
            name='handphone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
