# Sistem Manajemen Hotel

Aplikasi web untuk mengelola hotel. Tamu bisa melihat kamar yang tersedia, melakukan booking, dan membayar. Admin bisa mengelola data kamar, melihat booking, mengatur banner, dan menangani pesan kontak.

## Fitur Utama

### Untuk Tamu
- Lihat daftar kamar tersedia dengan gambar dan harga
- Cari kamar berdasarkan nomor atau tipe
- Lihat detail lengkap setiap kamar termasuk fasilitas
- Booking kamar dengan mengisi form pemesanan
- Konfirmasi pembayaran setelah booking
- Cetak struk pembayaran
- Kirim pesan ke hotel melalui form kontak

### Untuk Admin
- Kelola data kamar: tambah, edit, hapus
- Upload gambar untuk setiap kamar
- Atur banner yang muncul di homepage
- Set detail tipe kamar (Standard, Deluxe, Suite, VIP) termasuk fasilitas dan keuntungan
- Lihat semua booking tamu
- Baca pesan kontak dari tamu
- Login dengan autentikasi sederhana
- Pagination dan pencarian untuk memudahkan navigasi data

## Teknologi yang Digunakan

- Python 3 dengan Flask untuk backend
- SQLite untuk database
- HTML, CSS, JavaScript untuk frontend
- Bootstrap 5.3 untuk styling
- Font Awesome untuk icon
- Werkzeug untuk handling file upload

## Struktur Folder

```
uas-hotel-project/
├── app.py                 # Main Flask application
├── database/
│   └── hotel.db          # SQLite database
├── static/
│   ├── css/
│   │   ├── admin.css     # Admin page styles
│   │   └── theme.css     # User page styles
│   ├── images/
│   │   └── kamar/        # Room images
│   ├── img/              # Banner images
│   └── js/
│       └── theme.js      # Theme JavaScript
└── templates/
    ├── admin/            # Admin templates
    └── user/             # User templates
```

## Instalasi dan Menjalankan

Pastikan sudah install Python 3.7 atau lebih baru.

1. Clone atau download project ini

2. Buat virtual environment (disarankan):
```bash
python -m venv venv
```

3. Aktifkan virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install flask werkzeug
```

5. Jalankan aplikasi:
```bash
python app.py
```

6. Buka browser:
   - Halaman tamu: `http://127.0.0.1:5000`
   - Login admin: `http://127.0.0.1:5000/admin/login`

## Konfigurasi

### Login Admin Default
- Username: `admin`
- Password: `admin123`

Ubah password ini setelah pertama kali login.

### Database
Database SQLite dibuat otomatis di folder `database/` saat aplikasi pertama kali jalan. Tabel yang dibuat:
- `kamar` - data kamar
- `booking` - data pemesanan
- `banner` - banner homepage
- `tipe_kamar_detail` - detail tipe kamar
- `kontak` - pesan tamu
- `admin` - data admin

### Upload File
- Gambar kamar: `static/images/kamar/`
- Gambar banner: `static/img/`
- Format yang didukung: jpg, jpeg, png, gif

## Cara Penggunaan

### Sebagai Tamu

Mulai dari halaman beranda. Kamu bisa lihat kamar yang tersedia, pakai fitur search kalau mau cari spesifik, lalu klik kamar yang menarik untuk lihat detail lengkapnya. Setelah itu isi form booking dengan data diri, konfirmasi pembayaran, dan simpan struknya.

### Sebagai Admin

Login dulu dengan kredensial default. Setelah masuk, kamu bisa:
- Kelola kamar di menu "Kamar" - tambah baru, edit yang ada, atau hapus
- Atur banner di menu "Banner" untuk tampilan homepage
- Set detail tipe kamar di "Detail Tipe" - isi informasi fasilitas, keuntungan, dan upload gambar
- Lihat booking tamu di menu "Booking"
- Baca pesan kontak di menu "Kontak"

Semua halaman admin punya fitur search dan pagination untuk memudahkan navigasi kalau datanya banyak.

## Lisensi

Belum ditentukan.
