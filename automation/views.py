import datetime

import jwt
import openpyxl
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import UploadedFile, LogHistory 


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


import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import UploadedFile


@login_required(login_url="login")
def input_data(request):
    errors = [] 

    if request.method == "POST":
        course_name = request.POST.get("course_name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        course_model = request.POST.get("course_model")
        destination = request.POST.get("destination")
        upload_file = request.FILES.get("file_upload")

        required_columns = [
            "No",
            "Nama",
            "Jenis_Kelamin",
            "NIK",
            "Tempat_Lahir",
            "Tanggal_Lahir",
            "NISN",
            "Agama_LKP",
            "Handphone",
            "Kewarganegaraan",
            "Jenis_Tinggal",
            "Tanggal_Masuk",
            "Email",
            "Nama_Ortu",
            "NIK_Ortu",
            "Pekerjaan_Ortu",
            "Pendidikan_Ortu",
            "Penghasilan_Ortu",
            "Handphone_Ortu",
            "Tempat_Lahir_Ortu",
            "Tanggal_Lahir_Ortu",
            "Asal",
            "Alamat",
            "RT",
            "RW",
            "Kecamatan",
            "Kelurahan",
            "Kab/Kota",
            "Propinsi",
            "Nama_Ibu_kandung",
            "Nama_Ayah",
            "Agama_Kemdikbud",
            "Penerima_KPS",
            "Layak_PIP",
            "Penerima_KIP",
            "Kode_Pos",
            "Jenis_tinggal",
            "Alat_Transportasi",
        ]

        if upload_file:
            try:
                df = pd.read_excel(upload_file, sheet_name="all", dtype=str)  # Paksa jadi string
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Hapus spasi tersembunyi

                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    errors.append(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")

                if not missing_columns:
                    df_required = df[required_columns].replace(["", " "], pd.NA)  # Ganti kosong ke pd.NA

                    # Periksa apakah ada baris yang memiliki setidaknya satu nilai kosong
                    empty_rows = df_required[df_required.isna().any(axis=1)]
                    
                    if not empty_rows.empty:
                        empty_row_indices = empty_rows.index + 2  # Menyesuaikan agar sesuai dengan nomor baris di Excel

                        if len(empty_row_indices) > 1:
                            errors.append(f"Ada lebih dari 1 baris yang memiliki setidaknya satu nilai kosong.")
                        else:
                            for index, row in empty_rows.iterrows():
                                empty_columns = row[row.isna()].index.tolist()
                                errors.append(f"Baris {index + 2} pada file memiliki sel kosong pada kolom: {', '.join(empty_columns)}")


                if errors:
                    return render(request, "input_data.html", {"errors": errors})

                # Jika semua baris lengkap, simpan ke database
                UploadedFile.objects.create(
                    course_name=course_name,
                    start_date=start_date,
                    end_date=end_date,
                    course_model=course_model,
                    destination=destination,
                    file=upload_file,
                )
                messages.success(request, "File berhasil diunggah dan validasi berhasil!")
                return redirect("input_data")

            except Exception as e:
                errors.append(f"Terjadi kesalahan saat membaca file: {str(e)}")
                return render(request, "input_data.html", {"errors": errors})



    return render(request, "input_data.html", {"errors": errors})


@login_required(login_url="login")
def upload_page(request):
    return render(request, "upload.html")


@login_required(login_url="login")
def otomatisasi(request):
    files = UploadedFile.objects.all()
    return render(request, "otomatisasi.html", {"files": files})

from django.utils.timezone import localtime
@login_required(login_url="login")
def log_history(request):
    logs = LogHistory.objects.all()
    for log in logs:
        log.local_time = localtime(log.upload_date).strftime("%d %b %Y %H:%M")
    return render(request, "log_history.html", {"logs": logs})


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

from django.shortcuts import get_object_or_404, redirect, render

from .forms import OtomatisasiForm
from .models import UploadedFile


@login_required(login_url='login')
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


from django.http import FileResponse, Http404
import os
@login_required(login_url="login")
def download_file(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    # Pastikan path file benar
    file_path = file_obj.file.path  
    if not os.path.exists(file_path):
        raise Http404("File tidak ditemukan.")

    # Kirim file sebagai respons HTTP
    response = FileResponse(open(file_path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response

import os
from django.conf import settings
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required(login_url="login")
def process_files(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            file_ids = data.get("file_ids", [])

            if not file_ids:
                return JsonResponse({"status": "error", "message": "No files selected."})

            files = UploadedFile.objects.filter(id__in=file_ids)
            file_paths = [file.file.path for file in files]

            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otomatisasi.py')
            
            if not os.path.exists(script_path):
                return JsonResponse({
                    "status": "error",
                    "message": "Script otomatisasi tidak ditemukan",
                    "detail": f"Path yang dicari: {script_path}"
                })

            result = subprocess.run(
                ["python", script_path] + file_paths,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            if result.returncode == 0:
                # Catat log history dan hapus dari otomatisasi
                for file in files:
                    LogHistory.objects.create(
                        name=os.path.basename(file.file.name),  # Nama file saja
                        upload_date=timezone.now(),
                        course_name=file.course_name,
                        status='Success',
                        process_time=timezone.now()
                    )
                    file.delete()  # Hapus dari tabel otomatisasi
                
                return JsonResponse({
                    "status": "success",
                    "message": f"Semua {len(file_paths)} file berhasil diproses!",
                    "output": result.stdout
                })
            else:
                # Hanya catat log error tanpa menghapus file
                for file in files:
                    LogHistory.objects.create(
                        name=os.path.basename(file.file.name),
                        upload_date=timezone.now(),
                        course_name=file.course_name,
                        status='Failed',
                        process_time=timezone.now()
                    )
                
                return JsonResponse({
                    "status": "error",
                    "message": "Terjadi kesalahan saat memproses file",
                    "detail": result.stderr,
                    "output": result.stdout
                })
                
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})