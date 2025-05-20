from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from automation import views as automation

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", automation.user_login, name="login"),
    path("login/", automation.user_login, name="login"),
    path("register/", automation.register, name="register"),
    path("homepage/", automation.homepage, name="homepage"),
    path("upload/", automation.upload_page, name="upload_page"),
    path("input_data/", automation.input_data, name="input_data"),
    path("otomatisasi/", automation.otomatisasi, name="otomatisasi"),
    path(
        "otomatisasi/delete/<int:id>/",
        automation.delete_otomatisasi,
        name="delete_otomatisasi",
    ),
    path(
        "otomatisasi/edit/<int:id>/",
        automation.edit_otomatisasi,
        name="edit_otomatisasi",
    ),
    path("log-history/", automation.log_history, name="log_history"),
    path("data_siswa/", automation.data_siswa, name="data_siswa"),
    path(
        "data_siswa/delete/<int:id>/",
        automation.delete_data_siswa_single,
        name="delete_data_siswa_single",
    ),
    path(
        "data_siswa/delete/",
        automation.delete_data_siswa,
        name="delete_data_siswa",
    ),
    path(
        "data_siswa/edit/<int:id>/",
        automation.edit_data_siswa,
        name="edit_data_siswa",
    ),
    path("logout/", automation.logoutview, name="logout"),
    path("forgot_pw/", automation.forgot_pw, name="forgot_pw"),
    path(
        "forgot-password-notif/",
        automation.forgot_password_notification,
        name="forgot_password_notif",
    ),
    path("reset-password/", automation.reset_password, name="reset_password"),
    path("verify/<str:token>/", automation.verify_email, name="verify_email"),
    path("process-files/", automation.process_files, name="process_files"),
    path("resume-process/", automation.resume_process, name="resume_process"),
    path("generate_document/", automation.generate_document, name="generate_document"),
    path("delete-peserta/", automation.delete_peserta, name="delete_peserta"),
    path("log-history2/", automation.log_history2, name="log_history2"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)