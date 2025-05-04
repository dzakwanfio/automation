import datetime
import json
import logging
import os
import re
import subprocess

import jwt
import openpyxl
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Setup logging untuk debugging
logging.basicConfig(
    filename='process_files.log',
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

from .forms import OtomatisasiForm
from .models import LogHistory, Otomatisasi, UploadedFile


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
                df = pd.read_excel(upload_file, sheet_name="all", dtype=str)
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    errors.append(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")

                if not missing_columns:
                    df_required = df[required_columns].replace(["", " "], pd.NA)

                    empty_rows = df_required[df_required.isna().any(axis=1)]
                    
                    if not empty_rows.empty:
                        empty_row_indices = empty_rows.index + 2

                        if len(empty_row_indices) > 1:
                            errors.append(f"Ada lebih dari 1 baris yang memiliki setidaknya satu nilai kosong.")
                        else:
                            for index, row in empty_rows.iterrows():
                                empty_columns = row[row.isna()].index.tolist()
                                errors.append(f"Baris {index + 2} pada file memiliki sel kosong pada kolom: {', '.join(empty_columns)}")

                if errors:
                    return render(request, "input_data.html", {"errors": errors})

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

    else:
        logging.info(f"Loading input_data page with GET request. URL: {request.path}, Referer: {request.META.get('HTTP_REFERER', 'Unknown')}")
        files = UploadedFile.objects.all()
        return render(request, "input_data.html", {"errors": errors, "files": files})
        
@login_required(login_url="login")
def upload_page(request):
    return render(request, "upload.html")

@login_required(login_url="login")
def otomatisasi(request):
    files = UploadedFile.objects.all()  # Ambil semua file yang belum dihapus
    logging.info(f"Files in otomatisasi view: {files.count()} files found")  # Tambah logging
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
def delete_otomatisasi(request, id):  # Ubah file_id menjadi id
    if request.method == "POST":
        try:
            file = UploadedFile.objects.get(id=id)
            file_path = file.file.path
            file.delete()
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"File deleted from disk: {file_path}")
            logging.info(f"Deleted UploadedFile entry with ID {id}")
            return JsonResponse({"status": "success", "message": "File deleted successfully"})
        except UploadedFile.DoesNotExist:
            logging.info(f"UploadedFile with ID {id} already deleted or not found")
            return JsonResponse({"status": "error", "message": "File not found"}, status=404)
        except Exception as e:
            logging.error(f"Error deleting file with ID {id}: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error deleting file: {str(e)}"}, status=500)
    else:
        logging.warning("Invalid method in delete_otomatisasi")
        return JsonResponse({"status": "error", "message": "Metode tidak diizinkan, gunakan POST"}, status=405)

@login_required(login_url="login")
def edit_otomatisasi(request, id):
    file_obj = get_object_or_404(UploadedFile, pk=id)
    if request.method == 'POST':
        form = OtomatisasiForm(request.POST, request.FILES, instance=file_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('otomatisasi')
    else:
        form = OtomatisasiForm(instance=file_obj)
    return render(request, 'edit_otomatisasi.html', {'form': form, 'file_obj': file_obj})

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

@login_required(login_url="login")
def download_file(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    file_path = file_obj.file.path  
    if not os.path.exists(file_path):
        raise Http404("File tidak ditemukan.")

    response = FileResponse(open(file_path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response

import json
import logging
import os
import shutil
import subprocess

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import LogHistory, UploadedFile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('process_files.log')])

@csrf_exempt
@login_required(login_url="login")
def process_files(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            file_ids = data.get("file_ids", [])

            # Tambahkan logging untuk melacak pemanggilan
            logging.info(f"process_files called with file_ids: {file_ids}, from URL: {request.path}, Referer: {request.META.get('HTTP_REFERER', 'Unknown')}")

            if not file_ids:
                logging.warning("No files selected in process_files")
                return JsonResponse({"status": "error", "message": "No files selected.", "last_row": 0}, status=400)

            files = UploadedFile.objects.filter(id__in=file_ids)
            if not files.exists():
                logging.warning("No valid files found for the given IDs")
                return JsonResponse({"status": "error", "message": "No valid files found.", "last_row": 0}, status=400)

            file_path_dict = {file.id: file.file.path for file in files}
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otomatisasi.py')
            
            if not os.path.exists(script_path):
                logging.error(f"Script not found at: {script_path}")
                return JsonResponse({
                    "status": "error",
                    "message": "Script otomatisasi tidak ditemukan",
                    "last_row": 0,
                    "detail": f"Path yang dicari: {script_path}"
                }, status=400)

            processed_files = []
            failed_files = []
            last_row = 0
            status = "success"
            message = "Semua file berhasil diproses!"

            # Direktori sementara untuk file yang gagal
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_failed_files')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            for file in files:
                file_path = file.file.path
                logging.info(f"Starting process for file: {file_path}, exists: {os.path.exists(file_path)}")
                try:
                    result = subprocess.run(
                        ["python", script_path, file_path],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.abspath(__file__)),
                        check=False,
                        timeout=600  # Batas waktu 10 menit untuk setiap file
                    )

                    logging.debug(f"Subprocess stdout for {file_path}: {result.stdout}")
                    logging.debug(f"Subprocess stderr for {file_path}: {result.stderr}")
                    logging.debug(f"Subprocess returncode for {file_path}: {result.returncode}")

                    script_output = {}
                    if result.stdout.strip():
                        try:
                            script_output = json.loads(result.stdout.strip())
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON decode error for {file_path}: {str(e)}")
                            script_output = {"status": "error", "message": "Gagal memproses output dari script otomatisasi"}

                    file_status = script_output.get("status", "error")
                    file_message = script_output.get("message", "Terjadi kesalahan saat memroses file")
                    last_row = script_output.get("last_row", 0)

                    # Salin file ke direktori sementara jika gagal
                    temp_file_path = file_path
                    if file_status != "success":
                        file_name = os.path.basename(file_path)
                        temp_file_path = os.path.join(temp_dir, file_name)
                        shutil.copy2(file_path, temp_file_path)
                        logging.info(f"File copied to temp location: {temp_file_path}")

                    # Simpan log dengan nama file (sesuai LogHistory.save())
                    LogHistory.objects.create(
                        name=os.path.basename(file.file.name),
                        upload_date=timezone.now(),
                        course_name=file.course_name,
                        status='Success' if file_status == "success" else f'Failed (Stopped at row {last_row})',
                        process_time=timezone.now(),
                        file_path=os.path.basename(file.file.name),  # Hanya nama file, sesuai LogHistory
                        file_id=file.id
                    )

                    if file_status == "success":
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logging.info(f"File deleted after successful processing: {file_path}")
                        except Exception as e:
                            logging.warning(f"Failed to delete file {file_path}: {e}")
                        file.delete()  # Ini akan menghapus file fisik karena delete() di model
                        logging.info(f"Removed UploadedFile entry for successful file: {file_path}")
                        processed_files.append(file.id)
                    else:
                        # Hanya hapus entri database, file sudah disalin
                        file.is_failed = True
                        file.last_processed_row = last_row
                        file.save()
                        file.delete()  # Ini akan menghapus file fisik asli, tapi kita punya salinan
                        logging.info(f"Removed UploadedFile entry for failed file: {file_path}, file preserved at: {temp_file_path}")
                        failed_files.append(file.id)
                        message = f"Process failed at file {os.path.basename(file_path)}: {file_message} (Stopped at row {last_row})"
                        status = "error"
                        break

                except subprocess.TimeoutExpired as e:
                    logging.error(f"Timeout processing file {file_path}: {str(e)}")
                    file_name = os.path.basename(file_path)
                    temp_file_path = os.path.join(temp_dir, file_name)
                    shutil.copy2(file_path, temp_file_path)
                    logging.info(f"File copied to temp location: {temp_file_path}")

                    LogHistory.objects.create(
                        name=os.path.basename(file.file.name),
                        upload_date=timezone.now(),
                        course_name=file.course_name,
                        status='Failed (Timeout)',
                        process_time=timezone.now(),
                        file_path=os.path.basename(file.file.name),
                        file_id=file.id
                    )
                    file.is_failed = True
                    file.last_processed_row = last_row
                    file.save()
                    file.delete()  # Ini akan menghapus file fisik asli, tapi kita punya salinan
                    logging.info(f"Removed UploadedFile entry for timed-out file: {file_path}, file preserved at: {temp_file_path}")
                    failed_files.append(file.id)
                    message = f"Timeout processing file {os.path.basename(file_path)}: Process took too long"
                    status = "error"
                    break
                except Exception as e:
                    logging.error(f"Unexpected error processing {file_path}: {str(e)}")
                    file_name = os.path.basename(file_path)
                    temp_file_path = os.path.join(temp_dir, file_name)
                    shutil.copy2(file_path, temp_file_path)
                    logging.info(f"File copied to temp location: {temp_file_path}")

                    LogHistory.objects.create(
                        name=os.path.basename(file.file.name),
                        upload_date=timezone.now(),
                        course_name=file.course_name,
                        status='Failed (Unexpected error)',
                        process_time=timezone.now(),
                        file_path=os.path.basename(file.file.name),
                        file_id=file.id
                    )
                    file.is_failed = True
                    file.last_processed_row = last_row
                    file.save()
                    file.delete()  # Ini akan menghapus file fisik asli, tapi kita punya salinan
                    logging.info(f"Removed UploadedFile entry for failed file with unexpected error: {file_path}, file preserved at: {temp_file_path}")
                    failed_files.append(file.id)
                    message = f"Unexpected error processing {os.path.basename(file_path)}: {str(e)}"
                    status = "error"
                    break

            remaining_files = [f for f in files if f.id not in processed_files and f.id not in failed_files]
            for remaining_file in remaining_files:
                logging.info(f"Retained unprocessed file: {remaining_file.file.path}")

            if status == "success":
                messages.success(request, f"{len(processed_files)} file berhasil diproses!")
            else:
                messages.error(request, message)

            logging.info(f"Returning response: status={status}, failed_file_ids={failed_files}")
            return JsonResponse({
                "status": status,
                "message": message,
                "last_row": last_row,
                "failed_file_ids": failed_files if failed_files else []
            }, status=200)

        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in request body: {str(e)}")
            return JsonResponse({"status": "error", "message": "Data request tidak valid", "last_row": 0}, status=400)
        except Exception as e:
            logging.error(f"Unexpected error in process_files: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error server: {str(e)}", "last_row": 0}, status=500)

    logging.warning("Invalid method in process_files")
    return JsonResponse({"status": "error", "message": "Metode tidak diizinkan", "last_row": 0}, status=405)

@csrf_exempt
@login_required(login_url="login")
def resume_process(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            log_id = data.get("log_id")

            # Tambahkan logging untuk melacak pemanggilan
            logging.info(f"resume_process called with log_id: {log_id}, from URL: {request.path}, Referer: {request.META.get('HTTP_REFERER', 'Unknown')}")

            if not log_id:
                logging.warning("No log_id provided in resume_process")
                return JsonResponse({"status": "error", "message": "No log ID provided.", "last_row": 0})

            log_entry = get_object_or_404(LogHistory, id=log_id)
            match = re.search(r"Stopped at row (\d+)", log_entry.status)
            if not match:
                logging.error(f"Could not extract last row from status: {log_entry.status}")
                return JsonResponse({
                    "status": "error",
                    "message": "Cannot determine the last processed row.",
                    "last_row": 0
                })

            last_row = int(match.group(1))
            if last_row < 1:
                last_row = 2

            # Bangun path lengkap dari file_path (hanya nama file)
            file_path = os.path.join(settings.MEDIA_ROOT, log_entry.file_path)
            logging.info(f"Resuming with file path: {file_path}, exists: {os.path.exists(file_path)}")
            if not os.path.exists(file_path):
                # Coba cari di temp_failed_files
                temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_failed_files', log_entry.file_path)
                if os.path.exists(temp_file_path):
                    file_path = temp_file_path
                    logging.info(f"File found in temp location: {file_path}")
                else:
                    logging.error(f"File not found at: {file_path} or {temp_file_path}")
                    return JsonResponse({
                        "status": "error",
                        "message": f"File tidak ditemukan di server. Pastikan file masih ada di lokasi: {file_path} atau {temp_file_path}",
                        "last_row": 0
                    })

            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otomatisasi.py')
            if not os.path.exists(script_path):
                logging.error(f"Script not found at: {script_path}")
                return JsonResponse({
                    "status": "error",
                    "message": "Script otomatisasi tidak ditemukan",
                    "last_row": 0,
                    "detail": f"Path yang dicari: {script_path}"
                })

            result = subprocess.run(
                ["python", script_path, file_path, "--resume-from", str(last_row)],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                timeout=600  # Batas waktu 10 menit untuk resume
            )

            logging.debug(f"Resume subprocess stdout: {result.stdout}")
            logging.debug(f"Resume subprocess stderr: {result.stderr}")
            logging.debug(f"Resume subprocess returncode: {result.returncode}")

            try:
                script_output = json.loads(result.stdout.strip())
                status = script_output.get("status", "error")
                message = script_output.get("message", "Terjadi kesalahan saat melanjutkan proses")
                last_row = script_output.get("last_row", last_row)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error in resume_process: {str(e)}")
                return JsonResponse({
                    "status": "error",
                    "message": "Gagal memproses output dari script otomatisasi",
                    "last_row": last_row,
                    "detail": result.stderr if result.stderr else "No stderr output"
                })

            if status == "success":
                log_entry.status = "Success"
                log_entry.process_time = timezone.now()
                log_entry.save()

                # Hapus file fisik setelah sukses
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"File deleted from disk after successful resume: {file_path}")

                logging.info(f"Successfully resumed processing for log ID {log_id}")
                return JsonResponse({
                    "status": "success",
                    "message": "Proses berhasil dilanjutkan dan selesai!",
                    "last_row": last_row
                })
            else:
                log_entry.status = f"Failed (Stopped at row {last_row})"
                log_entry.process_time = timezone.now()
                log_entry.save()

                logging.error(f"Resume process failed at row {last_row}: {message}")
                return JsonResponse({
                    "status": "error",
                    "message": message,
                    "last_row": last_row,
                    "detail": result.stderr if result.stderr else "No stderr output"
                })

        except subprocess.TimeoutExpired as e:
            logging.error(f"Timeout in resume_process for log_id {log_id}: {str(e)}")
            log_entry.status = "Failed (Timeout)"
            log_entry.process_time = timezone.now()
            log_entry.save()
            return JsonResponse({
                "status": "error",
                "message": "Timeout: Resume process took too long",
                "last_row": last_row
            })
        except Exception as e:
            logging.error(f"Unexpected error in resume_process: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e), "last_row": 0})

    logging.warning("Invalid method in resume_process")
    return JsonResponse({"status": "error", "message": "Metode tidak diizinkan", "last_row": 0})