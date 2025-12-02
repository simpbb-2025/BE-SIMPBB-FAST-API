# SIMPBB FastAPI

Backend FastAPI untuk SIMPBB: autentikasi JWT, manajemen pengguna, pendaftaran SPOP, lampiran LSPOP, pengelolaan SPPT, dashboard, dan dropdown referensi.

## Requirements
- Python 3.11+
- MySQL (skema `ipbb`)

## Setup Cepat
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API tersedia di prefix `/api`, dokumentasi interaktif di `http://localhost:8000/docs`.

## Database
- Wajib: tabel dasar pada `ipbb.sql` (termasuk `ipbb_user`, `sppt`, `sppt_report`, `spop`, referensi wilayah).
- Tambahan untuk verifikasi user:
  ```sql
  ALTER TABLE ipbb_user
    ADD COLUMN verification_code varchar(10) NULL AFTER password,
    ADD COLUMN verification_code_expires_at datetime NULL AFTER verification_code;
  ```
- Tambahan untuk alur SPOP/LSPOP:
  - `spop_registration`
  - `lampiran_spop`
  - Referensi kelas NJOP: `kelas_bumi_njop`, `kelas_bangunan_njop`

## Peran & Autentikasi
- Peran: `admin`, `staff`, `user`.
- `POST /auth/login` mengembalikan bearer token.
- Sebagian besar endpoint (kecuali login/registrasi) butuh header `Authorization: Bearer <token>`.

## Pola Respons
- Modul user/SPPT/SPOP/LSPOP: `{"status":"success","message": "...", "data": ...}` (+`meta.pagination` bila paginasi).
- Modul dropdown: `{"success": true, "message": "...", ...}`.

## Endpoint Utama (ringkas)

### Auth & Users
- `POST /auth/login`
- `POST /users/register` + `POST /users/register/request-code`
- `GET /users/profile/me`, `PATCH /users/profile/me`
- `GET/PUT/DELETE /users/{user_id}`
- `GET /users` (list, pagination)
- `POST /users` (buat admin/staff, hanya admin)

### Dropdown
- `GET /dropdown/spop` – wilayah + status_subjek + pekerjaan + jenis_tanah
- `GET /dropdown/alamat-subjek` – dropdown wilayah sederhana
- `GET /dropdown/lspop` – jenis/kondisi bangunan, kelas per sektor, dll.
- `GET /dropdown/kelas-njop` – daftar kelas bumi & bangunan NJOP (id, kelas, njop)

### SPOP (permohonan objek pajak baru)
- `POST /spop/requests` – buat permohonan (JSON atau form-data)
- `GET /spop/requests` – list (pagination)
- `GET /spop/requests/{id}` – detail
- `PUT/PATCH/POST /spop/requests/{id}` – update
- `DELETE /spop/requests/{id}` – hapus

### LSPOP (lampiran bangunan)
- `POST /lspop` – buat lampiran; otomatis membuat SPPT terkait
- `GET /lspop` – list (pagination, filter `nop`)
- `GET /lspop/{id}` – detail
- `PATCH/PUT/POST /lspop/{id}` – update
- `DELETE /lspop/{id}` – hapus

### SPPT
- `GET /sppt?nop=...` – daftar SPPT untuk NOP yang sama. Aturan total:
  - Bumi hanya sekali: `total_luas_bumi` memakai 1× luas_bumi, dan bumi_njop dipakai sekali di summary.
  - Bangunan dijumlahkan: `total_luas_bangunan` = Σ luas_bangunan per bangunan; bangunan_njop dijumlahkan per entri.
  - `total_njop` = (1× bumi_njop) + Σ bangunan_njop. `pbb_terhutang` summary dihitung dari total_njop (setelah njoptkp & pbb_persen).
  - Tiap item menampilkan: bumi_njop, bangunan_njop, luas_bumi, luas_bangunan, kelas_bumi_njop, kelas_bangunan_njop (objek id+kelas+njop).

## Catatan Payload
- Banyak endpoint menerima JSON; beberapa SPOP/LSPOP mendukung `multipart/form-data` / `application/x-www-form-urlencoded`.
- Untuk dropdown kelas NJOP, gunakan nilai `id` yang dikembalikan (bukan string nama) saat mengisi payload SPOP/LSPOP/SPPT.
