# Generated by Django 5.1.7 on 2025-03-24 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otomatisasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('tanggal', models.DateField()),
            ],
        ),
    ]
