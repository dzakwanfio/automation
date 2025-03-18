import datetime

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import *


@login_required(login_url="login")
def homepage(request):
    return render(request, "homepage.html")


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("homepage")

        messages.error(request, "Email atau password salah")

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi domain email
        # if not email.endswith("@trustunified.com"):
        #     messages.error(request, "Email menggunakan domain yang tidak valid")
        #     return redirect("register")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok")
            return redirect("register")

        if len(password) < 8:
            messages.error(request, "Password harus setidaknya 8 karakter")
            return redirect("register")

        # try:
        #     validate_password(password)
        # except ValidationError as e:
        #     messages.error(request, f"Password tidak valid: {' '.join(e.messages)}")
        #     return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar")
            return redirect("register")

        # Buat user dengan is_active=False sehingga belum bisa login
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        # Generate token verifikasi dengan email user (bisa juga menambahkan id jika diinginkan)
        token = generate_verification_token(email)

        verification_link = request.build_absolute_uri(
            reverse("verify_email", kwargs={"token": token})
        )
        email_subject = "Verifikasi Akun Anda"
        email_body = (
            f"Klik link berikut untuk mengaktifkan akun Anda: {verification_link}"
        )

        send_mail(
            email_subject,
            email_body,
            "your_email@gmail.com",
            [email],
            fail_silently=False,
        )

        messages.success(
            request, "Email verifikasi telah dikirim. Silakan cek inbox Anda."
        )
        return redirect("login")

    return render(request, "register.html")


def generate_verification_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=24),  # Token berlaku 24 jam
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_email(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload["email"]

        try:
            # Ambil user berdasarkan email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User tidak ditemukan. Silakan daftar ulang.")
            return redirect("register")

        if user.is_active:
            messages.error(request, "Email sudah diverifikasi sebelumnya.")
        else:
            user.is_active = True  # Aktifkan user
            user.save()
            messages.success(request, "Email berhasil diverifikasi! Silakan login.")

        return redirect("login")

    except jwt.ExpiredSignatureError:
        messages.error(request, "Token telah kedaluwarsa. Silakan daftar kembali.")
    except jwt.DecodeError:
        messages.error(request, "Token tidak valid.")

    return redirect("register")


@login_required(login_url="login")
def input_data(request):
    if request.method == "POST":
        course_name = request.POST.get("course_name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        course_model = request.POST.get("course_model")
        destination = request.POST.get("destination")
        upload_file = request.FILES.get("upload_file")

        # Simpan atau proses data sesuai kebutuhan
        print(f"Course Name: {course_name}, Start Date: {start_date}, End Date: {end_date}, Model: {course_model}, Destination: {destination}, File: {upload_file}")

        return HttpResponse("Form submitted successfully!")

    return render(request, "input_data.html")


@login_required(login_url="login")
def upload_page(request):
    return render(request, 'upload.html')


@login_required(login_url="login")
def otomatisasi(request):
    return render(request, 'otomatisasi.html', {
        'empty_rows': range(6)  # Mengirim list kosong dengan 6 elemen
    })


@login_required(login_url="login")
def log_history(request):
    return render(request, 'log_history.html')
# create a logout view


@login_required(login_url="login")
def logoutview(request):
    logout(request)
    return redirect('login')


def forgot_pw(request):
    return render(request, "forgot_pw.html")

def forgot_password_notification(request):
    return render(request, 'forgot_pwnotif.html')

def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            messages.success(request, "Password berhasil direset! Silakan login.")
            return redirect("login")
        else:
            messages.error(request, "Password tidak cocok. Silakan coba lagi.")

    return render(request, "reset_password.html")