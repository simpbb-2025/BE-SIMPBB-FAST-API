from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


JPB_REQUIRED_FIELDS: Dict[str, set[str]] = {
    "01": {"kd_dinding", "kd_lantai", "kd_langit_langit"},
    "02": {"jns_konstruksi_bng", "jns_atap_bng"},
    "03": {"jns_konstruksi_bng", "jml_lantai_bng", "nilai_sistem_bng"},
}


class LspopBasePayload(BaseModel):
    nop: Optional[str] = Field(
        default=None,
        description="NOP 18 digit tanpa pemisah. Jika tidak diisi, gunakan komponen kunci.",
    )
    kd_propinsi: Optional[str] = Field(default=None, min_length=2, max_length=6)
    kd_dati2: Optional[str] = Field(default=None, min_length=2, max_length=6)
    kd_kecamatan: Optional[str] = Field(default=None, min_length=3, max_length=9)
    kd_kelurahan: Optional[str] = Field(default=None, min_length=3, max_length=9)
    kd_blok: Optional[str] = Field(default=None, min_length=3, max_length=9)
    no_urut: Optional[str] = Field(default=None, min_length=1, max_length=12)
    kd_jns_op: Optional[str] = Field(default=None, min_length=1, max_length=2)

    no_bng: int = Field(ge=0, description="Nomor bangunan (NO_BNG)")
    kd_jpb: str = Field(min_length=1, max_length=3, description="Kode JPB")
    no_formulir_lspop: Optional[str] = Field(default=None, max_length=15)
    thn_dibangun_bng: Optional[str] = Field(default=None, max_length=4)
    thn_renovasi_bng: Optional[str] = Field(default=None, max_length=4)
    luas_bng: Optional[Decimal] = None
    jml_lantai_bng: Optional[int] = None
    kondisi_bng: Optional[str] = Field(default=None, max_length=2)
    jns_konstruksi_bng: Optional[str] = Field(default=None, max_length=2)
    jns_atap_bng: Optional[str] = Field(default=None, max_length=2)
    kd_dinding: Optional[str] = Field(default=None, max_length=2)
    kd_lantai: Optional[str] = Field(default=None, max_length=2)
    kd_langit_langit: Optional[str] = Field(default=None, max_length=2)
    nilai_sistem_bng: Optional[Decimal] = None
    jns_transaksi_bng: Optional[str] = Field(default=None, max_length=1)
    tgl_pendataan_bng: Optional[date] = None
    nip_pendata_bng: Optional[str] = Field(default=None, max_length=30)
    tgl_pemeriksaan_bng: Optional[date] = None
    nip_pemeriksa_bng: Optional[str] = Field(default=None, max_length=30)
    tgl_perekaman_bng: Optional[date] = None
    nip_perekam_bng: Optional[str] = Field(default=None, max_length=30)
    tgl_kunjungan_kembali: Optional[date] = None
    nilai_individu: Optional[Decimal] = None
    aktif: bool = Field(description="True jika bangunan aktif, False jika tidak")

    @model_validator(mode="after")
    def validate_keys(self) -> "LspopBasePayload":
        data = self.model_dump()
        if not data.get("nop"):
            components = [
                data.get("kd_propinsi"),
                data.get("kd_dati2"),
                data.get("kd_kecamatan"),
                data.get("kd_kelurahan"),
                data.get("kd_blok"),
                data.get("no_urut"),
                data.get("kd_jns_op"),
            ]
            if not all(components):
                raise ValueError(
                    "Isi NOP atau lengkapi komponen kunci (kd_propinsi, kd_dati2, kd_kecamatan, "
                    "kd_kelurahan, kd_blok, no_urut, kd_jns_op)"
                )
        return self


class LspopCreatePayload(LspopBasePayload):
    @model_validator(mode="after")
    def validate_jpb_specifics(self) -> "LspopCreatePayload":
        required = JPB_REQUIRED_FIELDS.get(self.kd_jpb)
        if required:
            missing = [field for field in required if getattr(self, field) in (None, "")]
            if missing:
                raise ValueError(
                    f"JPB {self.kd_jpb} membutuhkan field berikut: {', '.join(missing)}"
                )
        return self


class LspopDetail(BaseModel):
    kd_propinsi: str
    kd_dati2: str
    kd_kecamatan: str
    kd_kelurahan: str
    kd_blok: str
    no_urut: str
    kd_jns_op: str
    no_bng: int
    kd_jpb: Optional[str]
    no_formulir_lspop: Optional[str]
    thn_dibangun_bng: Optional[str]
    thn_renovasi_bng: Optional[str]
    luas_bng: Optional[Decimal]
    jml_lantai_bng: Optional[int]
    kondisi_bng: Optional[str]
    jns_konstruksi_bng: Optional[str]
    jns_atap_bng: Optional[str]
    kd_dinding: Optional[str]
    kd_lantai: Optional[str]
    kd_langit_langit: Optional[str]
    nilai_sistem_bng: Optional[Decimal]
    jns_transaksi_bng: Optional[str]
    tgl_pendataan_bng: Optional[date]
    nip_pendata_bng: Optional[str]
    tgl_pemeriksaan_bng: Optional[date]
    nip_pemeriksa_bng: Optional[str]
    tgl_perekaman_bng: Optional[date]
    nip_perekam_bng: Optional[str]
    tgl_kunjungan_kembali: Optional[date]
    nilai_individu: Optional[Decimal]
    aktif: bool


class LspopCreateResponse(BaseModel):
    success: bool = True
    message: str
    data: LspopDetail
