import datetime
import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import UploadedFile  # Menggunakan UploadedFile untuk upload dan delete


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

        if password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok")
            return redirect("register")

        if len(password) < 8:
            messages.error(request, "Password harus setidaknya 8 karakter")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar")
            return redirect("register")

        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        token = generate_verification_token(email)

        verification_link = request.build_absolute_uri(
            reverse("verify_email", kwargs={"token": token})
        )
        email_subject = "Verifikasi Akun Anda"
        email_body = f"Klik link berikut untuk mengaktifkan akun Anda: {verification_link}"

        send_mail(email_subject, email_body, "your_email@gmail.com", [email], fail_silently=False)

        messages.success(request, "Email verifikasi telah dikirim. Silakan cek inbox Anda.")
        return redirect("login")

    return render(request, "register.html")


def generate_verification_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_email(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload["email"]

        user = get_object_or_404(User, email=email)

        if user.is_active:
            messages.error(request, "Email sudah diverifikasi sebelumnya.")
        else:
            user.is_active = True
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
        upload_file = request.FILES.get("file_upload")

        print(f"Received: {course_name}, {start_date}, {end_date}, {course_model}, {destination}, {upload_file}")

        if upload_file:
            UploadedFile.objects.create(
                course_name=course_name,
                start_date=start_date,
                end_date=end_date,
                course_model=course_model,
                destination=destination,
                file=upload_file,
            )
            print("Data berhasil disimpan!")  # Tambahkan debug log
            messages.success(request, "File berhasil diunggah!")

        return redirect("input_data")

    return render(request, "input_data.html")


@login_required(login_url="login")
def upload_page(request):
    return render(request, "upload.html")


@login_required(login_url="login")
def otomatisasi(request):
    files = UploadedFile.objects.all()
    return render(request, "otomatisasi.html", {"files": files})


@login_required(login_url="login")
def log_history(request):
    return render(request, "log_history.html")


@login_required(login_url="login")
def logoutview(request):
    logout(request)
    return redirect("login")


def forgot_pw(request):
    return render(request, "forgot_pw.html")


def forgot_password_notification(request):
    return render(request, "forgot_pwnotif.html")


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


@login_required(login_url="login")
def delete_otomatisasi(request, id):
    item = get_object_or_404(UploadedFile, id=id)
    print(f"Deleting item with id {id}")  # Debug log
    item.delete()
    messages.success(request, "Data berhasil dihapus!")
    return redirect("otomatisasi")


@login_required(login_url="login")
def edit_otomatisasi(request, id):
    otomatisasi_item = get_object_or_404(UploadedFile, id=id)

    if request.method == "POST":
        otomatisasi_item.course_name = request.POST.get("course_name")
        otomatisasi_item.course_model = request.POST.get("course_model")
        otomatisasi_item.destination = request.POST.get("destination")
        otomatisasi_item.start_date = request.POST.get("start_date")
        otomatisasi_item.end_date = request.POST.get("end_date")
        otomatisasi_item.save()
        messages.success(request, "Data berhasil diperbarui!")
        return redirect("otomatisasi")

    return render(request, "edit_otomatisasi.html", {"otomatisasi": otomatisasi_item})


@login_required(login_url="login")
def upload_data(request):
    if request.method == "POST":
        course_name = request.POST.get("course_name")
        course_model = request.POST.get("course_model")

        if course_name and course_model:
            UploadedFile.objects.create(course_name=course_name, course_model=course_model)
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect("otomatisasi")

    return render(request, "upload.html")

from django.shortcuts import render, get_object_or_404, redirect
from .models import UploadedFile
from .forms import OtomatisasiForm

def edit_otomatisasi(request, id):
    file_obj = get_object_or_404(UploadedFile, pk=id)
    if request.method == 'POST':
        form = OtomatisasiForm(request.POST, request.FILES, instance=file_obj)
        if form.is_valid():
            form.save()
            return redirect('otomatisasi')  # Ubah 'otomatisasi_list' dengan URL name yang sesuai
    else:
        form = OtomatisasiForm(instance=file_obj)
    return render(request, 'edit_otomatisasi.html', {'form': form, 'file_obj': file_obj})

