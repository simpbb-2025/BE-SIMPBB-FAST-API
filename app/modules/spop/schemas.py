from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _strip_or_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


class PaginationLinks(BaseModel):
    prev: Optional[str]
    next: Optional[str]


class PaginationMeta(BaseModel):
    total: int
    limit: int
    page: int
    total_pages: int
    links: PaginationLinks


class SpopSearchItem(BaseModel):
    nop: str
    nama_wp: Optional[str]
    jalan_op: Optional[str]
    jns_transaksi_op: Optional[str]
    status: Optional[str]
    no_formulir_spop: Optional[str]


class SpopSearchData(BaseModel):
    items: List[SpopSearchItem]
    meta: PaginationMeta


class SpopSearchResponse(BaseModel):
    success: bool = True
    message: str
    data: SpopSearchData


class SpopBasePayload(BaseModel):
    subjek_pajak_id: str
    jns_transaksi_op: str = Field(min_length=1, max_length=1)
    jalan_op: str
    blok_kav_no_op: Optional[str] = None
    kelurahan_op: Optional[str] = None
    rw_op: Optional[str] = None
    rt_op: Optional[str] = None
    kd_status_wp: str = Field(min_length=1, max_length=1)
    luas_bumi: int
    kd_znt: Optional[str] = None
    jns_bumi: str = Field(min_length=1, max_length=1)
    nilai_sistem_bumi: int
    tgl_pendataan_op: date
    nm_pendataan_op: Optional[str] = None
    nip_pendata: Optional[str] = None
    tgl_pemeriksaan_op: date
    nm_pemeriksaan_op: Optional[str] = None
    nip_pemeriksa_op: Optional[str] = None
    no_persil: Optional[str] = None
    kd_propinsi_bersama: Optional[str] = None
    kd_dati2_bersama: Optional[str] = None
    kd_kecamatan_bersama: Optional[str] = None
    kd_kelurahan_bersama: Optional[str] = None
    kd_blok_bersama: Optional[str] = None
    no_urut_bersama: Optional[str] = None
    kd_jns_op_bersama: Optional[str] = None
    kd_propinsi_asal: Optional[str] = None
    kd_dati2_asal: Optional[str] = None
    kd_kecamatan_asal: Optional[str] = None
    kd_kelurahan_asal: Optional[str] = None
    kd_blok_asal: Optional[str] = None
    no_urut_asal: Optional[str] = None
    kd_jns_op_asal: Optional[str] = None
    no_sppt_lama: Optional[str] = None


class SpopCreatePayload(SpopBasePayload):
    nop: Optional[str] = None
    kd_propinsi: Optional[str] = None
    kd_dati2: Optional[str] = None
    kd_kecamatan: Optional[str] = None
    kd_kelurahan: Optional[str] = None
    kd_blok: Optional[str] = None
    no_urut: Optional[str] = None
    kd_jns_op: Optional[str] = None

    @model_validator(mode="after")
    def validate_keys(self) -> "SpopCreatePayload":
        filled_components = all(
            _strip_or_none(value)
            for value in (
                self.kd_propinsi,
                self.kd_dati2,
                self.kd_kecamatan,
                self.kd_kelurahan,
                self.kd_blok,
                self.no_urut,
                self.kd_jns_op,
            )
        )
        if not self.nop and not filled_components:
            raise ValueError("Nop atau komponen kunci harus diisi")
        return self


class SpopUpdatePayload(SpopBasePayload):
    @model_validator(mode="after")
    def ensure_changes(self) -> "SpopUpdatePayload":
        data = self.model_dump(exclude_unset=True)
        if len(data) == 0:
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class SpopDeleteResponse(BaseModel):
    success: bool = True
    message: str


class WilayahLabel(BaseModel):
    propinsi: Optional[str]
    dati2: Optional[str]
    kecamatan: Optional[str]
    kelurahan: Optional[str]


class SubjekPajakInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subjek_pajak_id: str
    nama: Optional[str]
    jalan: Optional[str]
    blok: Optional[str]
    rt: Optional[str]
    rw: Optional[str]
    kelurahan: Optional[str]
    kota: Optional[str]
    kode_pos: Optional[str]
    telepon: Optional[str]
    npwp: Optional[str]
    email: Optional[str]


class SpopDetail(BaseModel):
    nop: str
    kd_propinsi: str
    kd_dati2: str
    kd_kecamatan: str
    kd_kelurahan: str
    kd_blok: str
    no_urut: str
    kd_jns_op: str
    subjek_pajak: Optional[SubjekPajakInfo]
    wilayah: WilayahLabel
    no_formulir_spop: Optional[str]
    jns_transaksi_op: str
    jalan_op: str
    blok_kav_no_op: Optional[str]
    kelurahan_op: Optional[str]
    rw_op: Optional[str]
    rt_op: Optional[str]
    kd_status_wp: str
    luas_bumi: int
    kd_znt: Optional[str]
    jns_bumi: str
    nilai_sistem_bumi: int
    tgl_pendataan_op: date
    nm_pendataan_op: Optional[str]
    nip_pendata: Optional[str]
    tgl_pemeriksaan_op: date
    nm_pemeriksaan_op: Optional[str]
    nip_pemeriksa_op: Optional[str]
    no_persil: Optional[str]
    kd_propinsi_bersama: Optional[str]
    kd_dati2_bersama: Optional[str]
    kd_kecamatan_bersama: Optional[str]
    kd_kelurahan_bersama: Optional[str]
    kd_blok_bersama: Optional[str]
    no_urut_bersama: Optional[str]
    kd_jns_op_bersama: Optional[str]
    kd_propinsi_asal: Optional[str]
    kd_dati2_asal: Optional[str]
    kd_kecamatan_asal: Optional[str]
    kd_kelurahan_asal: Optional[str]
    kd_blok_asal: Optional[str]
    no_urut_asal: Optional[str]
    kd_jns_op_asal: Optional[str]
    no_sppt_lama: Optional[str]


class SpopDetailResponse(BaseModel):
    success: bool = True
    message: str
    data: SpopDetail


class SpopMutationResponse(BaseModel):
    success: bool = True
    message: str
    data: SpopDetail


class RiwayatEntry(BaseModel):
    aktivitas: str
    tanggal: date
    petugas: Optional[str]
    nip: Optional[str]


class RiwayatResponse(BaseModel):
    success: bool = True
    message: str
    items: List[RiwayatEntry]
