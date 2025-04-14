
# Import library yang diperlukan
import sys
import os
import openpyxl
import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def process_files(file_paths):
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
        else:
            logging.error("❌ Timeout: Login tidak terdeteksi dalam 2 menit.")
            driver.quit()
            return False

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
        except Exception as e:
            logging.error(f"❌ Gagal klik link 'Daftar Siswa Aktif': {e}")
            driver.quit()
            return False

        time.sleep(3)

        # Fungsi untuk mengubah nilai menjadi string aman
        def safe_str(value):
            try:
                return str(value).strip()
            except:
                return ""

        # Proses semua file yang dipilih
        for file_path in file_paths:
            try:
                logging.info(f"🔵 Memulai proses file: {file_path}")
                wb = load_workbook(file_path)
                sheet = wb.worksheets[0]

                # Looping untuk membaca data dari Excel
                i = 2
                while True:
                    if sheet[f"A{i}"].value is None or str(sheet[f"A{i}"].value).strip() == "":
                        break

                    try:
                        # Membaca data dari Excel
                        nama = safe_str(sheet[f"B{i}"].value)
                        jenis_kelamin = safe_str(sheet[f"C{i}"].value)
                        NIK = safe_str(sheet[f"D{i}"].value)
                        tempat_lahir = safe_str(sheet[f"E{i}"].value)
                        tanggal_lahir = safe_str(sheet[f"F{i}"].value)
                        NISN = safe_str(sheet["G" + str(i)].value)
                        Agama = safe_str(sheet["H" + str(i)].value)
                        Handphone = safe_str(sheet["I" + str(i)].value)
                        Kewarganeraan = safe_str(sheet["J" + str(i)].value)
                        Jenis_Tinggal = safe_str(sheet["K" + str(i)].value)
                        Tanggal_Masuk = safe_str(sheet["L" + str(i)].value)
                        Email = safe_str(sheet["M" + str(i)].value)
                        Nama_Ibu = safe_str(sheet["N" + str(i)].value)
                        NIK_Ibu = safe_str(sheet["O" + str(i)].value)
                        Pekerjaan_Ibu = safe_str(sheet["P" + str(i)].value)
                        Pendidikan_Ibu = safe_str(sheet["Q" + str(i)].value)
                        Penghasilan_Ibu = safe_str(sheet["R" + str(i)].value)
                        Handphone_Ibu = safe_str(sheet["S" + str(i)].value)
                        Tempat_Lahir_Ibu = safe_str(sheet["T" + str(i)].value)
                        Tanggal_Lahir_Ibu = safe_str(sheet["U" + str(i)].value)
                        Nama_Ayah = safe_str(Nama_Ibu)
                        NIK_Ayah = safe_str(NIK_Ibu)
                        Pekerjaan_Ayah = safe_str(Pekerjaan_Ibu)
                        Pendidikan_Ayah = safe_str(Pendidikan_Ibu)
                        Penghasilan_Ayah = safe_str(Penghasilan_Ibu)
                        Handphone_Ayah = safe_str(Handphone_Ibu)
                        Tempat_Lahir_Ayah = safe_str(Tempat_Lahir_Ibu)
                        Tanggal_Lahir_Ayah = safe_str(Tanggal_Lahir_Ibu)
                        Asal_Domisili = safe_str(sheet["V" + str(i)].value)
                        Alamat_Domisili = safe_str(sheet["W" + str(i)].value)
                        RT_Domisili = safe_str(sheet["X" + str(i)].value)
                        RW_Domisili = safe_str(sheet["Y" + str(i)].value)
                        Kecamatan_Domisili = safe_str(sheet["Z" + str(i)].value)
                        Kelurahan_Domisili = safe_str(sheet["AA" + str(i)].value)
                        Asal_KK = safe_str(Asal_Domisili)
                        Alamat_KK = safe_str(Alamat_Domisili)
                        RT_KK = safe_str(RT_Domisili)
                        RW_KK = safe_str(RW_Domisili)
                        Kecamatan_KK = safe_str(Kecamatan_Domisili)
                        Kelurahan_KK = safe_str(Kelurahan_Domisili)
                        logging.info(f"Memproses data: {nama}, {jenis_kelamin}, {NIK}, {tempat_lahir}, {tanggal_lahir}, {NISN}, {Agama}, {Handphone}, {Kewarganeraan}, {Jenis_Tinggal}, {Tanggal_Masuk}, {Email}, {Nama_Ibu}, {NIK_Ibu}, {Pekerjaan_Ibu}, {Pendidikan_Ibu}, {Penghasilan_Ibu}, {Handphone_Ibu}, {Tempat_Lahir_Ibu}, {Tanggal_Lahir_Ibu}, {Nama_Ayah}, {NIK_Ayah}, {Pekerjaan_Ayah}, {Pendidikan_Ayah}, {Penghasilan_Ayah}, {Handphone_Ayah}, {Tempat_Lahir_Ayah}, {Tanggal_Lahir_Ayah}, {Asal_Domisili}, {Alamat_Domisili}, {RT_Domisili}, {RW_Domisili}, {Kecamatan_Domisili}, {Kelurahan_Domisili}, {Asal_KK}, {Alamat_KK}, {RT_KK}, {RW_KK}, {Kecamatan_KK}, {Kelurahan_KK}")

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
                        driver.find_element(By.NAME, "nama_ibu").send_keys(Nama_Ibu)
                        driver.find_element(By.NAME, "nik_ibu").send_keys(NIK_Ibu)
                        driver.find_element(By.NAME, "pekerjaan_ibu").send_keys(Pekerjaan_Ibu)
                        driver.find_element(By.NAME, "pendidikan_ibu").send_keys(Pendidikan_Ibu)
                        driver.find_element(By.NAME, "penghasilan_ibu").send_keys(Penghasilan_Ibu)
                        driver.find_element(By.NAME, "hp_ibu").send_keys(Handphone_Ibu)
                        driver.find_element(By.NAME, "tempat_lahir_ibu").send_keys(Tempat_Lahir_Ibu)
                        driver.find_element(By.NAME, "tgl_lahir_ibu").send_keys(Tanggal_Lahir_Ibu)
                        driver.find_element(By.NAME, "nama_ayah").send_keys(Nama_Ayah)
                        driver.find_element(By.NAME, "nik_ayah").send_keys(NIK_Ayah)
                        driver.find_element(By.NAME, "pekerjaan_ayah").send_keys(Pekerjaan_Ayah)
                        driver.find_element(By.NAME, "pendidikan_ayah").send_keys(Pendidikan_Ayah)
                        driver.find_element(By.NAME, "penghasilan_ayah").send_keys(Penghasilan_Ayah)
                        driver.find_element(By.NAME, "hp_ayah").send_keys(Handphone_Ayah)
                        driver.find_element(By.NAME, "tempat_lahir_ayah").send_keys(Tempat_Lahir_Ayah)
                        driver.find_element(By.NAME, "tgl_lahir_ayah").send_keys(Tanggal_Lahir_Ayah)
                        driver.find_element(By.NAME, "asal_domisili").send_keys(Asal_Domisili)
                        driver.find_element(By.NAME, "alamat_domisili").send_keys(Alamat_Domisili)
                        driver.find_element(By.NAME, "rt_domisili").send_keys(RT_Domisili)
                        driver.find_element(By.NAME, "rw_domisili").send_keys(RW_Domisili)
                        driver.find_element(By.NAME, "kecamatan_domisili").send_keys(Kecamatan_Domisili)
                        driver.find_element(By.NAME, "kelurahan_domisili").send_keys(Kelurahan_Domisili)
                        driver.find_element(By.NAME, "asal_kk").send_keys(Asal_KK)
                        driver.find_element(By.NAME, "alamat_kk").send_keys(Alamat_KK)
                        driver.find_element(By.NAME, "rt_kk").send_keys(RT_KK)
                        driver.find_element(By.NAME, "rw_kk").send_keys(RW_KK)
                        driver.find_element(By.NAME, "kecamatan_kk").send_keys(Kecamatan_KK)
                        driver.find_element(By.NAME, "kelurahan_kk").send_keys(Kelurahan_KK)
                        
                        driver.find_element(By.XPATH, "//button[@type='submit']").click()  # Klik tombol submit
                    except NoSuchElementException as e:
                        logging.error(f"❌ Element tidak ditemukan pada baris {i}: {e}")
                    except TimeoutException as e:
                        logging.error(f"❌ Timeout pada baris {i}: {e}")
                    except Exception as e:
                        logging.error(f"❌ Error tidak terduga pada baris {i}: {e}") 

                    i += 1

                logging.info(f"✅ File {file_path} berhasil diproses!")
            
                
            except Exception as e:
                logging.error(f"❌ Error saat memproses file {file_path}: {e}")
                continue

        logging.info("✅ Semua file telah diproses!")
        input("🔚 Tekan Enter untuk menutup browser...")

        if data.get("status") == "success":
            driver.quit() 

        return True
        
    except Exception as e:
        logging.error(f"❌ Error utama: {e}")
        return False

if __name__ == "__main__":
    # Debugging info
    print("=== DEBUG INFO ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    print(f"Args received: {sys.argv}")
    
    if len(sys.argv) < 2:
        print("Error: No file paths provided")
        sys.exit(1)
    
    # Verifikasi file input
    for i, file_path in enumerate(sys.argv[1:]):
        if not os.path.exists(file_path):
            print(f"Error: File {i+1} not found - {file_path}")
            sys.exit(1)
        print(f"File {i+1} found: {file_path}")
    
    print("=================")
    
    # Jalankan proses utama
    process_files(sys.argv[1:])
