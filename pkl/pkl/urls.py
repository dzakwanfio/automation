"""
URL configuration for pkl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from automation import views as automation
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from automation.views import verify_email


urlpatterns = [
    path("verify/<str:token>/", verify_email, name="verify_email"),
    path("admin/", admin.site.urls),
    path("", automation.user_login, name="login"),
    path("login/", automation.user_login, name="login"),
    path(
        "homepage/", automation.homepage, name="homepage"
    ),  # Tambahkan path untuk homepage
    path("upload/", automation.upload_page, name="upload_page"),
    path("register/", automation.register, name="register"),
    path("forgot_pw/", automation.forgot_pw, name="forgot_pw"),
    path("input_data/", automation.input_data, name="input_data"),
    path("otomatisasi/", automation.otomatisasi, name="otomatisasi"),
    path("log-history/", automation.log_history, name="log_history"),
    path("logout/", automation.logoutview, name="logout"),
]
