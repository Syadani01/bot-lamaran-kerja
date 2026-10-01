import smtplib
import os
import time
import schedule
from datetime import datetime
import pytz  # Untuk memastikan zona waktu WIB
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# =====================================================================
# ISI DATA PRIBADI & PENGATURAN KEMAANAN
# =====================================================================

# 1. Data Profil Anda (Sudah Disesuaikan)
NAMA_ANDA = "Abdul Mughni Sukma Sadani"
NOMOR_HP = "0895383240554"
EMAIL_PENGIRIM = "ghonia021@gmail.com"

# 2. PENTING: Isi 16 digit App Password (Sandi Aplikasi) Google Anda di bawah ini
# Ganti teks "" dengan kode dari Akun Google Anda
PASSWORD_PENGIRIM = "abcd efgh ijkl mnop" 

# 3. Pengaturan File Lampiran CV PDF
# Pastikan berkas CV Anda disimpan di folder Download HP dengan nama ini
PATH_CV = "/storage/emulated/0/Download/CV_Abdul_Mughni.pdf"
NAMA_FILE_CV = "CV Terbaru Abdul (2).pdf"

# 4. Daftar Perusahaan Tujuan & Jadwal Kirim (Sudah Disesuaikan)
DAFTAR_TARGET = {
    "09:00": {
        "perusahaan": "PT Armada Footwear Indonesia",
        "emails_hrd": ["armadafootwearindonesia@gmail.com", "recruitment.afi@huali-group.com"],
        "posisi": "Operator produksi"
    },
    "11:00": {
        "perusahaan": "PT Armada Footwear Indonesia",
        "emails_hrd": ["armadafootwearindonesia@gmail.com", "recruitment.afi@huali-group.com"],
        "posisi": "Operator produksi"
    },
    "14:00": {
        "perusahaan": "PT Armada Footwear Indonesia",
        "emails_hrd": ["armadafootwearindonesia@gmail.com", "recruitment.afi@huali-group.com"],
        "posisi": "Operator produksi"
    }
}

# =====================================================================
# SISTEM OTOMATISASI UTAMA
# =====================================================================
def kirim_email(data_perusahaan, jam_kirim):
    wib = pytz.timezone('Asia/Jakarta')
    waktu_sekarang = datetime.now(wib).strftime('%H:%M:%S')
    
    perusahaan = data_perusahaan["perusahaan"]
    emails_hrd = data_perusahaan["emails_hrd"]
    posisi = data_perusahaan["posisi"]

    print(f"\n[{waktu_sekarang}] Memulai pengiriman otomatis jadwal jam {jam_kirim} WIB...")
    print(f"Target: {perusahaan} -> Mengirim ke: {', '.join(emails_hrd)}")

    # Membuat struktur dasar email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_PENGIRIM
    msg['To'] = ", ".join(emails_hrd)  # Mengirimkan ke kedua email sekaligus
    msg['Subject'] = f"Lamaran Pekerjaan - {posisi} - {NAMA_ANDA}"

    isi_email = f"""Dengan hormat,

Bapak/Ibu Tim HRD
{perusahaan}

Melalui email ini, saya bermaksud untuk melamar pekerjaan pada posisi {posisi} di perusahaan yang Bapak/Ibu pimpin. 

Sebagai bahan pertimbangan, bersama email ini saya lampirkan berkas Curriculum Vitae (CV) serta dokumen pendukung lainnya dalam format PDF yang merangkum kualifikasi dan pengalaman profesional saya.

Besar harapan saya untuk diberikan kesempatan ke tahap wawancara agar dapat mendiskusikan bagaimana kontribusi saya dapat mendukung visi dan misi {perusahaan}.

Demikian surat lamaran ini saya sampaikan. Terima kasih banyak atas waktu dan perhatian Bapak/Ibu.

Hormat saya,

{NAMA_ANDA}
No. HP/WhatsApp: {NOMOR_HP}
"""
    msg.attach(MIMEText(isi_email, 'plain'))

    # Memuat berkas CV PDF
    try:
        with open(PATH_CV, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {NAMA_FILE_CV}")
        msg.attach(part)
        print("-> File CV berhasil dimuat.")
    except FileNotFoundError:
        print(f"❌ Gagal: File CV tidak ditemukan di '{PATH_CV}'.")
        print("Pastikan nama file di folder Download HP Anda adalah 'CV_Abdul_Mughni.pdf'")
        return

    # Proses koneksi dan pengiriman SMTP Google
    try:
        print("-> Menghubungkan ke server Google...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_PENGIRIM, PASSWORD_PENGIRIM)
        
        print("-> Sedang mengirimkan email...")
        server.sendmail(EMAIL_PENGIRIM, emails_hrd, msg.as_string())
        server.quit()
        print(f"👉 BERHASIL! Email lamaran berhasil dikirim ke {perusahaan} pada jam {jam_kirim}.")
    except Exception as e:
        print(f"❌ Gagal mengirim email. Pastikan App Password benar. Error: {e}")

def jalankan_jadwal():
    wib = pytz.timezone('Asia/Jakarta')
    jam_menit_sekarang = datetime.now(wib).strftime("%H:%M")
    
    if jam_menit_sekarang in DAFTAR_TARGET:
        data_kirim = DAFTAR_TARGET[jam_menit_sekarang]
        kirim_email(data_kirim, jam_menit_sekarang)
        time.sleep(60)  # Mengunci selama 1 menit agar tidak duplikat kirim

schedule.every(1).minutes.do(jalankan_jadwal)

print("🤖 Bot Email Aktif & Standby!")
print(f"Menggunakan akun: {EMAIL_PENGIRIM}")
print("Menunggu waktu pengiriman otomatis (WIB):")
for jam, info in DAFTAR_TARGET.items():
    print(f" - Jam {jam} -> {info['perusahaan']} ({info['posisi']})")
print("\n[PENTING] Jangan tutup Termux & aktifkan WakeLock agar bot tetap berjalan.")

while True:
    schedule.run_pending()
    time.sleep(10)
