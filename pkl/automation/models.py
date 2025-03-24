import os
from django.db import models

class UploadedFile(models.Model):
    course_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    course_model = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    file = models.FileField(upload_to="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name
    def delete(self, *args, **kwargs):
        # Hapus file dari sistem file jika ada
        if self.file:
            file_path = self.file.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)

from django.db import models

class Otomatisasi(models.Model):
    file = models.FileField(upload_to="", null=True, blank=True)  # Bisa kosong sementara
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    course_name = models.CharField(max_length=255, default="Unknown Course")  # Default
    course_model = models.CharField(max_length=255, default="General")  # Default

    def __str__(self):
        return self.course_name
    