from django.contrib import admin
from .models import UploadedFile, Otomatisasi  # Import model
from django.utils import timezone

admin.site.register(UploadedFile)  # Daftarkan model
admin.site.register(Otomatisasi)   # Daftarkan model

class LogHistoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'local_upload_date')
    
    def local_upload_date(self, obj):
        return timezone.localtime(obj.upload_date)
    local_upload_date.short_description = 'Waktu Upload'