from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class LampiranCreatePayload(BaseModel):
    nop: str = Field(max_length=50)
    jumlah_bangunan: Optional[int] = None
    bangunan_ke: Optional[int] = None

    jenis_penggunaan_bangunan: Optional[int] = None
    kondisi_bangunan: Optional[int] = None
    tahun_dibangun: Optional[int] = None
    tahun_direnovasi: Optional[int] = None
    luas_bangunan_m2: Optional[int] = None
    jumlah_lantai: Optional[int] = None
    daya_listrik_watt: Optional[int] = None

    jenis_konstruksi: Optional[int] = None
    jenis_atap: Optional[int] = None
    jenis_lantai: Optional[int] = None
    jenis_langit_langit: Optional[int] = None

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

    kelas_bangunan_perkantoran: Optional[int] = None
    kelas_bangunan_ruko: Optional[int] = None
    kelas_bangunan_rumah_sakit: Optional[int] = None
    luas_ruang_kamar_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_olahraga: Optional[int] = None

    jenis_hotel: Optional[int] = None
    bintang_hotel: Optional[int] = None
    jumlah_kamar_hotel: Optional[int] = None
    luas_ruang_kamar_hotel_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_hotel_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_parkir: Optional[int] = None

    kelas_bangunan_apartemen: Optional[int] = None
    jumlah_kamar_apartemen: Optional[int] = None

    letak_tangki_minyak: Optional[int] = None
    kapasitas_tangki_minyak_liter: Optional[int] = None

    kelas_bangunan_sekolah: Optional[int] = None

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
    spop_id: Optional[str] = None

    nop: Optional[str] = None
    jumlah_bangunan: Optional[int] = None
    bangunan_ke: Optional[int] = None

    jenis_penggunaan_bangunan: Optional["StatusInfo"] = None
    kondisi_bangunan: Optional["StatusInfo"] = None
    tahun_dibangun: Optional[int] = None
    tahun_direnovasi: Optional[int] = None
    luas_bangunan_m2: Optional[int] = None
    jumlah_lantai: Optional[int] = None
    daya_listrik_watt: Optional[int] = None

    jenis_konstruksi: Optional["StatusInfo"] = None
    jenis_atap: Optional["StatusInfo"] = None
    jenis_lantai: Optional["StatusInfo"] = None
    jenis_langit_langit: Optional["StatusInfo"] = None

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

    kelas_bangunan_perkantoran: Optional["StatusInfo"] = None
    kelas_bangunan_ruko: Optional["StatusInfo"] = None
    kelas_bangunan_rumah_sakit: Optional["StatusInfo"] = None
    luas_ruang_kamar_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_olahraga: Optional["StatusInfo"] = None

    jenis_hotel: Optional["StatusInfo"] = None
    bintang_hotel: Optional["StatusInfo"] = None
    jumlah_kamar_hotel: Optional[int] = None
    luas_ruang_kamar_hotel_ac_sentral_m2: Optional[int] = None
    luas_ruang_lain_hotel_ac_sentral_m2: Optional[int] = None

    kelas_bangunan_parkir: Optional["StatusInfo"] = None

    kelas_bangunan_apartemen: Optional["StatusInfo"] = None
    jumlah_kamar_apartemen: Optional[int] = None

    letak_tangki_minyak: Optional["StatusInfo"] = None
    kapasitas_tangki_minyak_liter: Optional[int] = None

    kelas_bangunan_sekolah: Optional["StatusInfo"] = None

    foto_objek_pajak: Optional[str] = None


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class SpptAutoRecord(BaseModel):
    id: str
    spop_id: str
    lspop_id: str
    nop: str
    bumi_njop: int
    bangunan_njop: int
    total_njop: int
    njoptkp: int
    pbb_persen_id: int
    pbb_persen: float
    pbb_terhutang: int
    create_at: datetime


class LampiranResponse(BaseModel):
    success: bool = True
    message: str
    data: LampiranRecord
    sppt: Optional[SpptAutoRecord] = None


class LampiranListResponse(BaseModel):
    success: bool = True
    message: str
    data: List[LampiranRecord]
    meta: Pagination


class LampiranDeleteResponse(BaseModel):
    success: bool = True
    message: str


class StatusInfo(BaseModel):
    id: Optional[int] = None
    nama: Optional[str] = None
