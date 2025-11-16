# SIMPBB FastAPI

FastAPI backend untuk dataset SIMPBB dengan autentikasi JWT, modul users, dashboard SPPT, dan layanan SPOP/SPPT berbasis NOP.

## Requirements

- Python 3.11+
- MySQL dengan skema `ipbb` sesuai `ipbb.sql`

## Installation

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Database

Aplikasi memakai tabel bawaan pada `ipbb.sql`, termasuk `ipbb_user`, `sppt`, `sppt_report`, `spop`, dan referensi wilayah. Pastikan tabel `ipbb_user` memiliki kolom tambahan untuk menyimpan kode verifikasi plaintext (varchar(10) + expiry):

```
ALTER TABLE ipbb_user
  ADD COLUMN verification_code varchar(10) NULL AFTER password,
  ADD COLUMN verification_code_expires_at datetime NULL AFTER verification_code;
```

## Running the server

```
uvicorn app.main:app --reload
```

API tersedia di prefix `/api`, dengan dokumentasi interaktif di `http://localhost:8000/docs`.

## Konfigurasi CORS

Nilai default di `.env` mengizinkan semua origin dan kredensial. Anda bisa menyesuaikan dengan variabel:
- `CORS_ORIGINS` contoh: `["http://localhost:3000"]`
- `CORS_ALLOW_METHODS` contoh: `["GET", "POST"]`
- `CORS_ALLOW_HEADERS` contoh: `["Authorization", "Content-Type"]`
- `CORS_ALLOW_CREDENTIALS` (True/False)

## Peran (role) dan flag boolean

- `role`: salah satu dari `admin`, `staff`, atau `user`.
  - Endpoint admin `POST /users` dipakai untuk menambah `admin` atau `staff`.
  - Endpoint publik `POST /users/register` dipakai untuk mendaftar `user`.
- Kolom `is_active` dan `is_verified` dalam request users bisa dikirim sebagai angka `0` atau `1`. Aplikasi akan mengonversi ke boolean sebelum disimpan, dan respons menampilkan `true/false`.

## Registrasi publik dengan kode verifikasi

- Atur konfigurasi SMTP pada `.env` (MAIL\_\*, USE\_CREDENTIALS). Endpoint `POST /users/register` secara otomatis akan mengirim kode verifikasi ke email yang didaftarkan.
- Saat registrasi, akun baru disimpan dengan `is_active = 0` dan `is_verified = 0`, serta kode verifikasi 7 karakter alfanumerik + waktu kedaluwarsa di kolom `verification_code*` pada tabel `ipbb_user`.
- Pengguna harus mengirim `POST /users/register/request-code` dengan payload `{ "email": "...", "verification_code": "..." }`. Endpoint ini akan membandingkan kode yang disimpan pada database dan, jika cocok serta belum kedaluwarsa, mengaktifkan akun (`is_active = is_verified = 1`).
- Jika kode salah atau kedaluwarsa, API mengembalikan HTTP 400 dengan pesan yang sesuai. Panjang kode default 7 karakter (`REGISTRATION_CODE_LENGTH`) dan berlaku 10 menit (`REGISTRATION_CODE_EXPIRE_MINUTES`).

## Format respons

Setiap endpoint sukses mengikuti pola:

```
{
  "status": "success",
  "message": "...",
  "data": ...,
  "meta": {
    "pagination": {
      "total": <int>,
      "page": <int>,
      "limit": <int>,
      "pages": <int>,
      "has_next": <bool>,
      "has_prev": <bool>
    }
  }
}
```

`meta.pagination` hanya muncul pada endpoint yang mengembalikan daftar.

## Endpoint utama

Semua endpoint di bawah membutuhkan bearer token kecuali `POST /auth/login`.

- `POST /auth/login` – body JSON `{ "username": "...", "password": "..." }`, mengembalikan token.
- `GET /users/profile/me` – profil pengguna yang sedang login.
- `PATCH /users/profile/me` – perbarui data diri pengguna yang sedang login.
- `GET /users/{user_id}` - detail pengguna berdasarkan UUID; hanya pemilik akun.
- `PUT /users/{user_id}` - perbarui data pengguna; hanya pemilik akun (tidak bisa ubah role/flags).
- `DELETE /users/{user_id}` - hapus pengguna; pemilik akun atau admin.
- `GET /users/` - daftar seluruh pengguna dengan pagination (`page`, `limit`); tidak ada validasi role.
- `POST /users/` - buat admin/staff baru (field `role`); hanya admin.
- `POST /users/register` - registrasi publik; sistem mengirim kode verifikasi ke email dan akun dibuat dengan status non-aktif sampai diverifikasi.
- `POST /users/register/request-code` - kirim email + kode verifikasi untuk mengaktifkan akun (menyetel `is_active` dan `is_verified` menjadi `true` jika kode cocok).
- `GET /dashboard/sppt/stats` – statistik SPPT (jumlah SPPT, bangunan, luas, nilai, wilayah) dengan filter `year`, `kd_propinsi`, `kd_dati2`, `kd_kecamatan`, `kd_kelurahan`.
- `GET /dashboard/sppt/filters` – opsi filter wilayah dan daftar tahun SPPT.
- `GET /dashboard/sppt-report/filters` – filter laporan SPPT (15 tahun terakhir, daftar kecamatan, default tahun maksimum).
- `GET /dashboard/sppt-report/data` – data laporan SPPT (table + statistik + yearly chart) dengan filter tahun, kecamatan, dan pagination (`page`, `limit`).
- `POST /sppt/verifikasi` – verifikasi data SPOP dan Subjek Pajak berdasarkan NOP dan (opsional) Subjek Pajak ID.
- `GET /sppt/spop` – daftar objek pajak dengan pagination, pencarian, dan sorting.
- `POST /sppt/years` – daftar tahun SPPT untuk NOP tertentu.
- `GET /sppt/{year}/{nop}` – detail SPPT berdasarkan tahun dan NOP.
- `GET /sppt/batch/{nop}` – semua SPPT untuk satu NOP.

