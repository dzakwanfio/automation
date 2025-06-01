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
    is_failed = models.BooleanField(default=False)
    last_processed_row = models.IntegerField(default=0)

    def __str__(self):
        return self.course_name

    def delete(self, *args, **kwargs):
        if self.file and self.file.path:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class Peserta(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, null=True, blank=True)
    nama = models.CharField(max_length=100)
    tempat_lahir = models.CharField(max_length=100, blank=True, null=True)
    tanggal_lahir = models.DateField(blank=True, null=True)
    jenis_kelamin = models.CharField(max_length=10, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    nomor_hp = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, blank=True, null=True)
    pendidikan_terakhir = models.CharField(max_length=100, blank=True, null=True)
    nama_lembaga = models.CharField(max_length=255, blank=True, null=True)
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    alamat_kantor = models.TextField(blank=True, null=True)
    telp_kantor = models.CharField(max_length=15, blank=True, null=True)
    kota = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_converted = models.BooleanField(default=False)

    def __str__(self):
        return self.nama

class Otomatisasi(models.Model):
    file = models.FileField(upload_to="", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    course_name = models.CharField(max_length=255, default="Unknown Course")
    course_model = models.CharField(max_length=255, default="General")
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.course_name

    def delete(self, *args, **kwargs):
        if self.file and self.file.path:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class LogHistory(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(default=timezone.now, db_index=True)
    course_name = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default='Success')
    process_time = models.DateTimeField(default=timezone.now)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    file_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.file_path and self.name:
            self.file_path = self.name
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-upload_date']

class Siswa(models.Model):
    nama = models.CharField(max_length=100)
    nikp = models.CharField(max_length=20, unique=True)
    jenis_kelamin = models.CharField(max_length=10)
    alamat = models.TextField()
    nomor_hp = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama

    class Meta:
        ordering = ['-created_at']

class LogHistory2(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    handphone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    course_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    process_time = models.DateTimeField(default=timezone.now)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_id = models.IntegerField(blank=True, null=True)
    jadwal = models.CharField(max_length=100, blank=True, null=True)
    tuk = models.CharField(max_length=100, blank=True, null=True)
    skema = models.CharField(max_length=100, blank=True, null=True)
    asesor = models.CharField(max_length=100, blank=True, null=True)
    lokasi_sertif = models.CharField(max_length=100, blank=True, null=True)
    template = models.CharField(max_length=50, blank=True, null=True)  # Tambahkan field ini

    def __str__(self):
        return self.name
