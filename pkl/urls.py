from django.contrib import admin
from django.urls import path
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
    path("otomatisasi/delete/<int:id>/", automation.delete_otomatisasi, name="delete_otomatisasi"),
    path("otomatisasi/edit/<int:id>/", automation.edit_otomatisasi, name="edit_otomatisasi"),
    path("log-history/", automation.log_history, name="log_history"),
    path("logout/", automation.logoutview, name="logout"),
    path("forgot_pw/", automation.forgot_pw, name="forgot_pw"),
    path("forgot-password-notif/", automation.forgot_password_notification, name='forgot_password_notif'),
    path("reset-password/", automation.reset_password, name="reset_password"),
    path("verify/<str:token>/", automation.verify_email, name="verify_email"),
]