from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class LampiranCreatePayload(BaseModel):
    nop: str = Field(max_length=50)
    jumlah_bangunan: Optional[int] = None
    bangunan_ke: Optional[int] = None

    jenis_penggunaan_bangunan: Optional[str] = Field(default=None, max_length=100)
    kondisi_bangunan: Optional[str] = Field(default=None, max_length=100)
    tahun_dibangun: Optional[int] = None
    tahun_direnovasi: Optional[int] = None
    luas_bangunan_m2: Optional[int] = None
    jumlah_lantai: Optional[int] = None
    daya_listrik_watt: Optional[int] = None

    jenis_konstruksi: Optional[str] = Field(default=None, max_length=100)
    jenis_atap: Optional[str] = Field(default=None, max_length=100)
    jenis_lantai: Optional[str] = Field(default=None, max_length=100)
    jenis_langit_langit: Optional[str] = Field(default=None, max_length=100)

    jumlah_ac: Optional[int] = None
    jumlah_ac_split: Optional[int] = None
    jumlah_ac_window: Optional[int] = None
    ac_sentral: Optional[bool] = None

    luas_kolam_renang_m2: Optional[int] = None
    kolam_renang_diplester: Optional[bool] = None
    kolam_renang_dengan_pelapis: Optional[bool] = None

    tenis_lampu_beton: Optional[int] = None
    tenis_lampu_aspal: Optional[int] = None
    tenis_lampu_tanah_liat: Optional[int] = None

    tenis_tanpa_lampu_beton: Optional[int] = None
    tenis_tanpa_lampu_aspal: Optional[int] = None
    tenis_tanpa_lampu_tanah_liat: Optional[int] = None

    jumlah_lift_penumpang: Optional[int] = None
    jumlah_lift_kapsul: Optional[int] = None
    jumlah_lift_barang: Optional[int] = None

    jumlah_tangga_berjalan_lebar_kurang_80_cm: Optional[int] = None
    jumlah_tangga_berjalan_lebar_lebih_80_cm: Optional[int] = None

    panjang_pagar_meter: Optional[int] = None
    pagar_bahan_baja_besi: Optional[bool] = None
    pagar_bahan_bata_batako: Optional[bool] = None

    pemadam_hydrant: Optional[bool] = None
    pemadam_sprinkler: Optional[bool] = None
    pemadam_fire_alarm: Optional[bool] = None

    kedalaman_sumur_artesis_meter: Optional[int] = None

    kelas_bangunan_perkantoran: Optional[str] = Field(default=None, max_length=100)
    kelas_bangunan_ruko: Optional[str] = Field(default=None, max_length=100)
    kelas_bangunan_rumah_sakit: Optional[str] = Field(default=None, max_length=100)
    luas_ruang_kamar_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_olahraga: Optional[str] = Field(default=None, max_length=100)

    jenis_hotel: Optional[str] = Field(default=None, max_length=100)
    bintang_hotel: Optional[str] = Field(default=None, max_length=50)
    jumlah_kamar_hotel: Optional[int] = None
    luas_ruang_kamar_hotel_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_hotel_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_parkir: Optional[str] = Field(default=None, max_length=100)

    kelas_bangunan_apartemen: Optional[str] = Field(default=None, max_length=100)
    jumlah_kamar_apartemen: Optional[int] = None

    letak_tangki_minyak: Optional[str] = Field(default=None, max_length=100)
    kapasitas_tangki_minyak_liter: Optional[int] = None

    kelas_bangunan_sekolah: Optional[str] = Field(default=None, max_length=100)

    foto_objek_pajak: Optional[str] = Field(default=None, max_length=255)


class LampiranUpdatePayload(LampiranCreatePayload):
    @model_validator(mode="after")
    def ensure_changes(self) -> "LampiranUpdatePayload":
        data = self.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class LampiranRecord(BaseModel):
    id: str
    submitted_at: datetime

    nop: Optional[str] = None
    jumlah_bangunan: Optional[int] = None
    bangunan_ke: Optional[int] = None

    jenis_penggunaan_bangunan: Optional[str] = None
    kondisi_bangunan: Optional[str] = None
    tahun_dibangun: Optional[int] = None
    tahun_direnovasi: Optional[int] = None
    luas_bangunan_m2: Optional[int] = None
    jumlah_lantai: Optional[int] = None
    daya_listrik_watt: Optional[int] = None

    jenis_konstruksi: Optional[str] = None
    jenis_atap: Optional[str] = None
    jenis_lantai: Optional[str] = None
    jenis_langit_langit: Optional[str] = None

    jumlah_ac: Optional[int] = None
    jumlah_ac_split: Optional[int] = None
    jumlah_ac_window: Optional[int] = None
    ac_sentral: Optional[bool] = None

    luas_kolam_renang_m2: Optional[int] = None
    kolam_renang_diplester: Optional[bool] = None
    kolam_renang_dengan_pelapis: Optional[bool] = None

    tenis_lampu_beton: Optional[int] = None
    tenis_lampu_aspal: Optional[int] = None
    tenis_lampu_tanah_liat: Optional[int] = None

    tenis_tanpa_lampu_beton: Optional[int] = None
    tenis_tanpa_lampu_aspal: Optional[int] = None
    tenis_tanpa_lampu_tanah_liat: Optional[int] = None

    jumlah_lift_penumpang: Optional[int] = None
    jumlah_lift_kapsul: Optional[int] = None
    jumlah_lift_barang: Optional[int] = None

    jumlah_tangga_berjalan_lebar_kurang_80_cm: Optional[int] = None
    jumlah_tangga_berjalan_lebar_lebih_80_cm: Optional[int] = None

    panjang_pagar_meter: Optional[int] = None
    pagar_bahan_baja_besi: Optional[bool] = None
    pagar_bahan_bata_batako: Optional[bool] = None

    pemadam_hydrant: Optional[bool] = None
    pemadam_sprinkler: Optional[bool] = None
    pemadam_fire_alarm: Optional[bool] = None

    kedalaman_sumur_artesis_meter: Optional[int] = None

    kelas_bangunan_perkantoran: Optional[str] = None
    kelas_bangunan_ruko: Optional[str] = None
    kelas_bangunan_rumah_sakit: Optional[str] = None
    luas_ruang_kamar_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_olahraga: Optional[str] = None

    jenis_hotel: Optional[str] = None
    bintang_hotel: Optional[str] = None
    jumlah_kamar_hotel: Optional[int] = None
    luas_ruang_kamar_hotel_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_hotel_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_parkir: Optional[str] = None

    kelas_bangunan_apartemen: Optional[str] = None
    jumlah_kamar_apartemen: Optional[int] = None

    letak_tangki_minyak: Optional[str] = None
    kapasitas_tangki_minyak_liter: Optional[int] = None

    kelas_bangunan_sekolah: Optional[str] = None

    foto_objek_pajak: Optional[str] = None


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class LampiranResponse(BaseModel):
    success: bool = True
    message: str
    data: LampiranRecord


class LampiranListResponse(BaseModel):
    success: bool = True
    message: str
    data: List[LampiranRecord]
    meta: Pagination


class LampiranDeleteResponse(BaseModel):
    success: bool = True
    message: str
