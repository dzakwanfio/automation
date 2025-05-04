# Import library yang diperlukan
import argparse
import json
import logging
import os
import sys
import time

import openpyxl
import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        NoSuchWindowException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Setup logging ke file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("otomatisasi.log"),
    ]
)

def process_files(file_paths, resume_from=2):
    # Validasi resume_from
    if not isinstance(resume_from, int) or resume_from < 1 or resume_from > 1048576:
        logging.error(f"Nilai resume_from tidak valid: {resume_from}. Harus antara 1 dan 1048576.")
        result = {"status": "error", "message": f"resume_from harus antara 1 dan 1048576. Nilai yang diberikan adalah {resume_from}", "last_row": 0}
        print(json.dumps(result))
        return result

    driver = None
    try:
        # Inisialisasi WebDriver Edge
        driver = webdriver.Edge()
        driver.get("https://lkpdispendik.surabaya.go.id/")
        logging.info("✅ Silakan login di browser... Menunggu hingga login selesai...")

        # Tunggu user login
        max_wait = 120
        wait_time = 0
        while wait_time < max_wait:
            try:
                driver.find_element(
                    By.XPATH,
                    "//a[@href='https://lkpdispendik.surabaya.go.id/dasboard/siswa/view/list/aktif?id=966']",
                )
                logging.info("✅ Login terdeteksi! Melanjutkan otomatisasi...")
                break
            except NoSuchElementException:
                time.sleep(2)
                wait_time += 2
            except (NoSuchWindowException, WebDriverException) as e:
                logging.error(f"❌ Browser ditutup atau tidak dapat diakses: {e}")
                result = {"status": "error", "message": "Browser ditutup sebelum login selesai", "last_row": 0}
                print(json.dumps(result))
                return result
        else:
            logging.error("❌ Timeout: Login tidak terdeteksi dalam 2 menit.")
            result = {"status": "error", "message": "Timeout: Login tidak terdeteksi dalam 2 menit", "last_row": 0}
            print(json.dumps(result))
            return result

        # Klik link ke halaman daftar siswa aktif
        try:
            link_daftar_siswa = driver.find_element(
                By.XPATH,
                "//a[@href='https://lkpdispendik.surabaya.go.id/dasboard/siswa/view/list/aktif?id=966']",
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_daftar_siswa)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", link_daftar_siswa)
            logging.info("✅ Berhasil klik link 'Daftar Siswa Aktif'")
        except (NoSuchElementException, NoSuchWindowException, WebDriverException) as e:
            logging.error(f"❌ Gagal klik link 'Daftar Siswa Aktif': {e}")
            result = {"status": "error", "message": f"Gagal mengakses halaman daftar siswa: {str(e)}", "last_row": 0}
            print(json.dumps(result))
            return result

        time.sleep(3)

        # Fungsi untuk mengubah nilai menjadi string aman
        def safe_str(value):
            try:
                return str(value).strip()
            except:
                return ""

        # Proses semua file yang dipilih
        for file_path in file_paths:
            logging.info(f"🔵 Memulai proses file: {file_path}, exists: {os.path.exists(file_path)}")
            try:
                wb = load_workbook(file_path)
                sheet = wb.worksheets[0]

                # Looping untuk membaca data dari Excel, mulai dari resume_from
                i = resume_from
                while True:
                    if sheet[f"A{i}"].value is None or str(sheet[f"A{i}"].value).strip() == "":
                        break

                    try:
                        # Membaca data dari Excel sesuai kolom di input_data
                        nama = safe_str(sheet[f"B{i}"].value)  # Nama
                        jenis_kelamin = safe_str(sheet[f"C{i}"].value)  # Jenis_Kelamin
                        NIK = safe_str(sheet[f"D{i}"].value)  # NIK
                        tempat_lahir = safe_str(sheet[f"E{i}"].value)  # Tempat_Lahir
                        tanggal_lahir = safe_str(sheet[f"F{i}"].value)  # Tanggal_Lahir
                        NISN = safe_str(sheet[f"G{i}"].value)  # NISN
                        Agama = safe_str(sheet[f"H{i}"].value)  # Agama_LKP
                        Handphone = safe_str(sheet[f"I{i}"].value)  # Handphone
                        Kewarganeraan = safe_str(sheet[f"J{i}"].value)  # Kewarganegaraan
                        Jenis_Tinggal = safe_str(sheet[f"K{i}"].value)  # Jenis_Tinggal
                        Tanggal_Masuk = safe_str(sheet[f"L{i}"].value)  # Tanggal_Masuk
                        Email = safe_str(sheet[f"M{i}"].value)  # Email
                        Nama_Ortu = safe_str(sheet[f"N{i}"].value)  # Nama_Ortu
                        NIK_Ortu = safe_str(sheet[f"O{i}"].value)  # NIK_Ortu
                        Pekerjaan_Ortu = safe_str(sheet[f"P{i}"].value)  # Pekerjaan_Ortu
                        Pendidikan_Ortu = safe_str(sheet[f"Q{i}"].value)  # Pendidikan_Ortu
                        Penghasilan_Ortu = safe_str(sheet[f"R{i}"].value)  # Penghasilan_Ortu
                        Handphone_Ortu = safe_str(sheet[f"S{i}"].value)  # Handphone_Ortu
                        Tempat_Lahir_Ortu = safe_str(sheet[f"T{i}"].value)  # Tempat_Lahir_Ortu
                        Tanggal_Lahir_Ortu = safe_str(sheet[f"U{i}"].value)  # Tanggal_Lahir_Ortu
                        Asal = safe_str(sheet[f"V{i}"].value)  # Asal
                        Alamat = safe_str(sheet[f"W{i}"].value)  # Alamat
                        RT = safe_str(sheet[f"X{i}"].value)  # RT
                        RW = safe_str(sheet[f"Y{i}"].value)  # RW
                        Kecamatan = safe_str(sheet[f"Z{i}"].value)  # Kecamatan
                        Kelurahan = safe_str(sheet[f"AA{i}"].value)  # Kelurahan
                        Kab_Kota = safe_str(sheet[f"AB{i}"].value)  # Kab/Kota
                        Propinsi = safe_str(sheet[f"AC{i}"].value)  # Propinsi
                        Nama_Ibu_kandung = safe_str(sheet[f"AD{i}"].value)  # Nama_Ibu_kandung
                        Nama_Ayah = safe_str(sheet[f"AE{i}"].value)  # Nama_Ayah
                        Agama_Kemdikbud = safe_str(sheet[f"AF{i}"].value)  # Agama_Kemdikbud
                        Penerima_KPS = safe_str(sheet[f"AG{i}"].value)  # Penerima_KPS
                        Layak_PIP = safe_str(sheet[f"AH{i}"].value)  # Layak_PIP
                        Penerima_KIP = safe_str(sheet[f"AI{i}"].value)  # Penerima_KIP
                        Kode_Pos = safe_str(sheet[f"AJ{i}"].value)  # Kode_Pos
                        Jenis_tinggal = safe_str(sheet[f"AK{i}"].value)  # Jenis_tinggal
                        Alat_Transportasi = safe_str(sheet[f"AL{i}"].value)  # Alat_Transportasi

                        logging.info(f"Memproses data baris {i}: {nama}")

                        # Klik link ke halaman tambah siswa
                        link_tambah_siswa = driver.find_element(
                            By.XPATH,
                            "//a[@href='https://lkpdispendik.surabaya.go.id/dasboard/siswa/view/tambah_siswa']",
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", link_tambah_siswa
                        )
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", link_tambah_siswa)

                        # Isi form tambah siswa
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="listar-content"]')
                            )
                        )
                        driver.find_element(By.NAME, "nama").send_keys(nama)
                        driver.find_element(By.NAME, "jenis_kelamin").send_keys(jenis_kelamin)
                        driver.find_element(By.NAME, "nik").send_keys(NIK)
                        driver.find_element(By.NAME, "tempat_lahir").send_keys(tempat_lahir)
                        driver.find_element(By.NAME, "tgl_lahir").send_keys(tanggal_lahir)
                        driver.find_element(By.NAME, "nisn").send_keys(NISN)
                        driver.find_element(By.NAME, "agama").send_keys(Agama)
                        driver.find_element(By.NAME, "hp").send_keys(Handphone)
                        driver.find_element(By.NAME, "kewarganegaraan").send_keys(Kewarganeraan)
                        driver.find_element(By.NAME, "jenis_tinggal").send_keys(Jenis_Tinggal)
                        driver.find_element(By.NAME, "tgl_masuk").send_keys(Tanggal_Masuk)
                        driver.find_element(By.NAME, "email").send_keys(Email)
                        driver.find_element(By.NAME, "nama_ibu").send_keys(Nama_Ibu_kandung or Nama_Ortu)
                        driver.find_element(By.NAME, "nik_ibu").send_keys(NIK_Ortu)
                        driver.find_element(By.NAME, "pekerjaan_ibu").send_keys(Pekerjaan_Ortu)
                        driver.find_element(By.NAME, "pendidikan_ibu").send_keys(Pendidikan_Ortu)
                        driver.find_element(By.NAME, "penghasilan_ibu").send_keys(Penghasilan_Ortu)
                        driver.find_element(By.NAME, "hp_ibu").send_keys(Handphone_Ortu)
                        driver.find_element(By.NAME, "tempat_lahir_ibu").send_keys(Tempat_Lahir_Ortu)
                        driver.find_element(By.NAME, "tgl_lahir_ibu").send_keys(Tanggal_Lahir_Ortu)
                        driver.find_element(By.NAME, "nama_ayah").send_keys(Nama_Ayah or Nama_Ortu)
                        driver.find_element(By.NAME, "nik_ayah").send_keys(NIK_Ortu)
                        driver.find_element(By.NAME, "pekerjaan_ayah").send_keys(Pekerjaan_Ortu)
                        driver.find_element(By.NAME, "pendidikan_ayah").send_keys(Pendidikan_Ortu)
                        driver.find_element(By.NAME, "penghasilan_ayah").send_keys(Penghasilan_Ortu)
                        driver.find_element(By.NAME, "hp_ayah").send_keys(Handphone_Ortu)
                        driver.find_element(By.NAME, "tempat_lahir_ayah").send_keys(Tempat_Lahir_Ortu)
                        driver.find_element(By.NAME, "tgl_lahir_ayah").send_keys(Tanggal_Lahir_Ortu)
                        driver.find_element(By.NAME, "asal_domisili").send_keys(Asal)
                        driver.find_element(By.NAME, "alamat_domisili").send_keys(Alamat)
                        driver.find_element(By.NAME, "rt_domisili").send_keys(RT)
                        driver.find_element(By.NAME, "rw_domisili").send_keys(RW)
                        driver.find_element(By.NAME, "kecamatan_domisili").send_keys(Kecamatan)
                        driver.find_element(By.NAME, "kelurahan_domisili").send_keys(Kelurahan)
                        driver.find_element(By.NAME, "asal_kk").send_keys(Asal)
                        driver.find_element(By.NAME, "alamat_kk").send_keys(Alamat)
                        driver.find_element(By.NAME, "rt_kk").send_keys(RT)
                        driver.find_element(By.NAME, "rw_kk").send_keys(RW)
                        driver.find_element(By.NAME, "kecamatan_kk").send_keys(Kecamatan)
                        driver.find_element(By.NAME, "kelurahan_kk").send_keys(Kelurahan)

                        driver.find_element(By.XPATH, "//button[@type='submit']").click()
                        logging.info(f"✅ Baris {i} berhasil diproses")
                    except (NoSuchWindowException, WebDriverException) as e:
                        logging.error(f"❌ Browser ditutup pada baris {i}: {e}")
                        result = {"status": "error", "message": f"Terdeteksi berhenti pada baris {i}", "last_row": i}
                        print(json.dumps(result))
                        return result
                    except (NoSuchElementException, TimeoutException) as e:
                        logging.error(f"❌ Gagal memproses baris {i}: {e}")
                        result = {"status": "error", "message": f"Gagal memproses baris {i}: {str(e)}", "last_row": i}
                        print(json.dumps(result))
                        return result
                    except Exception as e:
                        logging.error(f"❌ Error tidak terduga pada baris {i}: {e}")
                        result = {"status": "error", "message": f"Error tidak terduga pada baris {i}: {str(e)}", "last_row": i}
                        print(json.dumps(result))
                        return result

                    i += 1

                logging.info(f"✅ File {file_path} selesai diproses, exists: {os.path.exists(file_path)}")
            
            except (NoSuchWindowException, WebDriverException) as e:
                logging.error(f"❌ Browser ditutup saat memproses file {file_path}: {e}")
                result = {"status": "error", "message": f"Terdeteksi berhenti pada baris {i}", "last_row": i}
                print(json.dumps(result))
                return result
            except Exception as e:
                logging.error(f"❌ Error saat memproses file {file_path}: {e}")
                result = {"status": "error", "message": f"Error memproses file {file_path}: {str(e)}", "last_row": i}
                print(json.dumps(result))
                return result

        logging.info("✅ Semua file telah diproses!")
        result = {"status": "success", "message": f"Semua {len(file_paths)} file berhasil diproses!", "last_row": i}
        print(json.dumps(result))
        return result

    except (NoSuchWindowException, WebDriverException) as e:
        logging.error(f"❌ Browser ditutup: {e}")
        result = {"status": "error", "message": "Browser ditutup secara tidak sengaja", "last_row": 0}
        print(json.dumps(result))
        return result
    except Exception as e:
        logging.error(f"❌ Error utama: {e}")
        result = {"status": "error", "message": str(e), "last_row": 0}
        print(json.dumps(result))
        return result
    finally:
        if driver:
            try:
                logging.info("Attempting to close all windows and quit driver...")
                # Tutup semua jendela browser yang terbuka
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    driver.close()
                driver.quit()  # Pastikan driver benar-benar berhenti
                logging.info("Driver quit successfully.")
            except Exception as e:
                logging.error(f"Failed to quit driver: {e}")
                # Tidak perlu mengembalikan result lagi di sini karena sudah di-return di blok try/except

if __name__ == "__main__":
    # Parse argumen baris perintah
    parser = argparse.ArgumentParser(description="Script otomatisasi pengentry-an data siswa")
    parser.add_argument("file_paths", nargs='+', help="Path ke file Excel yang akan diproses")
    parser.add_argument("--resume-from", type=int, default=2, help="Baris mulai untuk melanjutkan proses")
    args = parser.parse_args()

    # Debugging info, dicetak ke stderr
    print("=== DEBUG INFO ===", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    print(f"Script location: {os.path.abspath(__file__)}", file=sys.stderr)
    print(f"Args received: {sys.argv}", file=sys.stderr)
    
    if len(args.file_paths) < 1:
        print(json.dumps({"status": "error", "message": "No file paths provided", "last_row": 0}))
        sys.exit(1)
    
    # Verifikasi file input
    for i, file_path in enumerate(args.file_paths):
        if not os.path.exists(file_path):
            print(json.dumps({"status": "error", "message": f"File {i+1} not found - {file_path}", "last_row": 0}))
            sys.exit(1)
        print(f"File {i+1} found: {file_path}", file=sys.stderr)
    
    print("=================", file=sys.stderr)
    
    # Jalankan proses utama
    process_files(args.file_paths, resume_from=args.resume_from)