from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages


def user_login(request):
    if request.method == "POST":
        return redirect('homepage')  # Langsung ke homepage tanpa autentikasi
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi domain email
        if not email.endswith("@trustunified.com"):
            messages.error(request, "Email harus menggunakan domain @trustunified.com")  # ✅ Tidak error lagi
            return redirect("register")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok")
            return redirect("register")

        # Cek apakah email sudah terdaftar
        if user.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar")
            return redirect("register")

        # Simpan user jika valid
        user = user.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(request, "Akun berhasil dibuat! Silakan login.")
        return redirect("login")

    return render(request, "register.html")


def forgot_pw(request):
    return render (request, 'forgot_pw.html')

def homepage(request):
    return render(request, 'homepage.html')

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


def upload_page(request):
    return render(request, 'upload.html')

def history(request):
    return render(request, 'history.html')

def otomatisasi(request):
    return render(request, 'otomatisasi.html', {
        'empty_rows': range(6)  # Mengirim list kosong dengan 6 elemen
    })
    
def log_history(request):
    return render(request, 'log_history.html')