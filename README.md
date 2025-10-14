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

Aplikasi memakai tabel bawaan pada `ipbb.sql`, termasuk `ipbb_user`, `sppt`, `sppt_report`, `spop`, dan referensi wilayah. Pastikan tabel `ipbb_user` memiliki kolom `username` unik sesuai konfigurasi.

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

## Format flag boolean

Kolom `is_active`, `is_verified`, dan `is_admin` dalam request users harus dikirim sebagai angka `0` atau `1`. Aplikasi akan mengonversi ke boolean sebelum disimpan, dan respons menampilkan `true/false`.

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
- `GET /users/{user_id}` – detail pengguna berdasarkan UUID; hanya pemilik atau admin.
- `PUT /users/{user_id}` – perbarui data pengguna; pemilik akun atau admin.
- `DELETE /users/{user_id}` – hapus pengguna; hanya admin (mengembalikan pesan sukses).
- `GET /users/` – daftar seluruh pengguna dengan pagination (`page`, `limit`, default limit 10); hanya admin.
- `POST /users/` – buat pengguna baru; hanya admin.
- `GET /dashboard/sppt/stats` – statistik SPPT (jumlah SPPT, bangunan, luas, nilai, wilayah) dengan filter `year`, `kd_propinsi`, `kd_dati2`, `kd_kecamatan`, `kd_kelurahan`.
- `GET /dashboard/sppt/filters` – opsi filter wilayah dan daftar tahun SPPT.
- `GET /dashboard/sppt-report/filters` – filter laporan SPPT (15 tahun terakhir, daftar kecamatan, default tahun maksimum).
- `GET /dashboard/sppt-report/data` – data laporan SPPT (table + statistik + yearly chart) dengan filter tahun, kecamatan, dan pagination (`page`, `limit`).
- `POST /sppt/verifikasi` – verifikasi data SPOP dan Subjek Pajak berdasarkan NOP dan (opsional) Subjek Pajak ID.
- `GET /sppt/spop` – daftar objek pajak dengan pagination, pencarian, dan sorting.
- `POST /sppt/years` – daftar tahun SPPT untuk NOP tertentu.
- `GET /sppt/{year}/{nop}` – detail SPPT berdasarkan tahun dan NOP.
- `GET /sppt/batch/{nop}` – semua SPPT untuk satu NOP.

