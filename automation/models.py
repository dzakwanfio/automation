import os

from django.db import models
from django.utils import timezone


class UploadedFile(models.Model):
    course_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    course_model = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    file = models.FileField(upload_to="") 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_failed = models.BooleanField(default=False)  # Menandai file yang gagal diproses
    last_processed_row = models.IntegerField(default=0)  # Baris terakhir yang diproses

    def __str__(self):
        return self.course_name

    def delete(self, *args, **kwargs):
        # Hapus file dari sistem file jika ada
        if self.file and self.file.path:  # Pastikan file ada sebelum dihapus
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class Otomatisasi(models.Model):
    file = models.FileField(upload_to="", null=True, blank=True) 
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    course_name = models.CharField(max_length=255, default="Unknown Course")  # Default
    course_model = models.CharField(max_length=255, default="General")  # Default
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.course_name
    
    def delete(self, *args, **kwargs):
        # Hapus file dari sistem file jika ada
        if self.file and self.file.path:  # Pastikan file ada sebelum dihapus
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
        

class LogHistory(models.Model):
    name = models.CharField(max_length=255)  # Nama file
    upload_date = models.DateTimeField(default=timezone.now, db_index=True)  # Tambahkan indeks
    course_name = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default='Success')  # Diperpanjang untuk status seperti "Failed (Stopped at row 123)"
    process_time = models.DateTimeField(default=timezone.now)
    file_path = models.CharField(max_length=255, null=True, blank=True)  # Kolom untuk menyimpan path relatif file
    file_id = models.IntegerField(null=True, blank=True)  # Tambahkan field ini
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Pastikan file_path diisi dengan path relatif jika belum ada
        # Karena upload_to="", file_path hanya menyimpan nama file tanpa prefiks 'uploads/'
        if not self.file_path and self.name:
            self.file_path = self.name  # Simpan hanya nama file
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-upload_date']  # Urutkan berdasarkan upload_date secara descending