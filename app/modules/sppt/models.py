from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, Numeric, String, DateTime, Enum
from datetime import datetime
from sqlmodel import Field, SQLModel

from app.modules.dashboards.models import Sppt  # Reuse existing SPPT model
from app.modules.users.models import User as UsersUser


class Spop(SQLModel, table=True):
    __tablename__ = "spop"

    kd_propinsi: str = Field(sa_column=Column("KD_PROPINSI", String(2), primary_key=True))
    kd_dati2: str = Field(sa_column=Column("KD_DATI2", String(2), primary_key=True))
    kd_kecamatan: str = Field(sa_column=Column("KD_KECAMATAN", String(3), primary_key=True))
    kd_kelurahan: str = Field(sa_column=Column("KD_KELURAHAN", String(3), primary_key=True))
    kd_blok: str = Field(sa_column=Column("KD_BLOK", String(3), primary_key=True))
    no_urut: str = Field(sa_column=Column("NO_URUT", String(4), primary_key=True))
    kd_jns_op: str = Field(sa_column=Column("KD_JNS_OP", String(1), primary_key=True))
    subjek_pajak_id: Optional[str] = Field(default=None, sa_column=Column("SUBJEK_PAJAK_ID", String(30)))
    no_formulir_spop: Optional[str] = Field(default=None, sa_column=Column("NO_FORMULIR_SPOP", String(11)))
    jalan_op: Optional[str] = Field(default=None, sa_column=Column("JALAN_OP", String(50)))
    blok_kav_no_op: Optional[str] = Field(default=None, sa_column=Column("BLOK_KAV_NO_OP", String(15)))
    kelurahan_op: Optional[str] = Field(default=None, sa_column=Column("KELURAHAN_OP", String(30)))
    rw_op: Optional[str] = Field(default=None, sa_column=Column("RW_OP", String(2)))
    rt_op: Optional[str] = Field(default=None, sa_column=Column("RT_OP", String(3)))
    kd_status_wp: Optional[str] = Field(default=None, sa_column=Column("KD_STATUS_WP", String(1)))
    luas_bumi: Optional[float] = Field(default=None, sa_column=Column("LUAS_BUMI", Numeric(18, 0)))
    kd_znt: Optional[str] = Field(default=None, sa_column=Column("KD_ZNT", String(3)))
    jns_bumi: Optional[str] = Field(default=None, sa_column=Column("JNS_BUMI", String(1)))


class DatSubjekPajak(SQLModel, table=True):
    __tablename__ = "dat_subjek_pajak"

    subjek_pajak_id: str = Field(sa_column=Column("SUBJEK_PAJAK_ID", String(30), primary_key=True))
    nm_wp: Optional[str] = Field(default=None, sa_column=Column("NM_WP", String(50)))
    jalan_wp: Optional[str] = Field(default=None, sa_column=Column("JALAN_WP", String(50)))
    blok_kav_no_wp: Optional[str] = Field(default=None, sa_column=Column("BLOK_KAV_NO_WP", String(15)))
    rw_wp: Optional[str] = Field(default=None, sa_column=Column("RW_WP", String(2)))
    rt_wp: Optional[str] = Field(default=None, sa_column=Column("RT_WP", String(3)))
    kelurahan_wp: Optional[str] = Field(default=None, sa_column=Column("KELURAHAN_WP", String(30)))
    kota_wp: Optional[str] = Field(default=None, sa_column=Column("KOTA_WP", String(30)))
    kd_pos_wp: Optional[str] = Field(default=None, sa_column=Column("KD_POS_WP", String(5)))
    telp_wp: Optional[str] = Field(default=None, sa_column=Column("TELP_WP", String(15)))
    npwp: Optional[str] = Field(default=None, sa_column=Column("NPWP", String(15)))
    status_pekerjaan_wp: Optional[str] = Field(default=None, sa_column=Column("STATUS_PEKERJAAN_WP", String(1)))
    email_wp: Optional[str] = Field(default=None, sa_column=Column("EMAIL_WP", String(50)))


User = UsersUser


class OpRegistration(SQLModel, table=True):
    __tablename__ = "op_registration"

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    submitted_at: Optional[datetime] = Field(
        default=None, sa_column=Column("submitted_at", DateTime, nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column("updated_at", DateTime, nullable=False)
    )
    status: Optional[str] = Field(
        default="submitted",
        sa_column=Column(
            "status",
            String(16),
            nullable=False,
        ),
    )
    notes: Optional[str] = Field(default=None, sa_column=Column("notes", String(2000)))

    submitted_by_user_id: Optional[str] = Field(
        default=None, sa_column=Column("submitted_by_user_id", String(32))
    )
    assigned_staff_id: Optional[str] = Field(
        default=None, sa_column=Column("assigned_staff_id", String(32))
    )
    processed_at: Optional[datetime] = Field(
        default=None, sa_column=Column("processed_at", DateTime)
    )

    # Data Pemohon
    nama_lengkap: Optional[str] = Field(default=None, sa_column=Column("nama_lengkap", String(255)))
    alamat_rumah: Optional[str] = Field(default=None, sa_column=Column("alamat_rumah", String(255)))
    telepon: Optional[str] = Field(default=None, sa_column=Column("telepon", String(50)))
    ktp: Optional[str] = Field(default=None, sa_column=Column("ktp", String(30)))

    # Data WP/OP
    nama_wp: str = Field(sa_column=Column("nama_wp", String(255), nullable=False))
    alamat_wp: str = Field(sa_column=Column("alamat_wp", String(255), nullable=False))
    alamat_op: str = Field(sa_column=Column("alamat_op", String(255), nullable=False))
    kd_propinsi: str = Field(sa_column=Column("kd_propinsi", String(2), nullable=False))
    kd_dati2: str = Field(sa_column=Column("kd_dati2", String(2), nullable=False))
    kd_kecamatan: str = Field(sa_column=Column("kd_kecamatan", String(3), nullable=False))
    kd_kelurahan: str = Field(sa_column=Column("kd_kelurahan", String(3), nullable=False))
    luas_bumi: int = Field(sa_column=Column("luas_bumi", Numeric(18, 0), nullable=False))
    luas_bangunan: int = Field(sa_column=Column("luas_bangunan", Numeric(18, 0), nullable=False))

    # Hasil proses
    subjek_pajak_id: Optional[str] = Field(default=None, sa_column=Column("subjek_pajak_id", String(30)))
    nop_assigned: Optional[str] = Field(default=None, sa_column=Column("nop_assigned", String(18)))

__all__ = [
    "Spop",
    "DatSubjekPajak",
    "Sppt",
    "OpRegistration",
    "User",
]
