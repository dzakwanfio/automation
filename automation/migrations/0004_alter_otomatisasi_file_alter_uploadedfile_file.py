# Generated by Django 5.1.7 on 2025-03-24 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0003_remove_otomatisasi_nama_remove_otomatisasi_tanggal_and_more'),
    ]

    operations = [
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
