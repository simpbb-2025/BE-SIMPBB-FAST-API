from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.modules.dashboards.models import RefDati2, RefKecamatan, RefKelurahan, RefPropinsi


class Spop(Base):
    __tablename__ = "spop"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(6), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(6), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(9), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(9), primary_key=True)
    kd_blok: Mapped[str] = mapped_column("KD_BLOK", String(9), primary_key=True)
    no_urut: Mapped[str] = mapped_column("NO_URUT", String(12), primary_key=True)
    kd_jns_op: Mapped[str] = mapped_column("KD_JNS_OP", String(1), primary_key=True)
    subjek_pajak_id: Mapped[str] = mapped_column("SUBJEK_PAJAK_ID", String(30), nullable=False)
    no_formulir_spop: Mapped[Optional[str]] = mapped_column("NO_FORMULIR_SPOP", String(11))
    jns_transaksi_op: Mapped[str] = mapped_column("JNS_TRANSAKSI_OP", String(1), nullable=False)
    kd_propinsi_bersama: Mapped[Optional[str]] = mapped_column("KD_PROPINSI_BERSAMA", String(2))
    kd_dati2_bersama: Mapped[Optional[str]] = mapped_column("KD_DATI2_BERSAMA", String(2))
    kd_kecamatan_bersama: Mapped[Optional[str]] = mapped_column("KD_KECAMATAN_BERSAMA", String(3))
    kd_kelurahan_bersama: Mapped[Optional[str]] = mapped_column("KD_KELURAHAN_BERSAMA", String(3))
    kd_blok_bersama: Mapped[Optional[str]] = mapped_column("KD_BLOK_BERSAMA", String(3))
    no_urut_bersama: Mapped[Optional[str]] = mapped_column("NO_URUT_BERSAMA", String(4))
    kd_jns_op_bersama: Mapped[Optional[str]] = mapped_column("KD_JNS_OP_BERSAMA", String(1))
    kd_propinsi_asal: Mapped[Optional[str]] = mapped_column("KD_PROPINSI_ASAL", String(2))
    kd_dati2_asal: Mapped[Optional[str]] = mapped_column("KD_DATI2_ASAL", String(2))
    kd_kecamatan_asal: Mapped[Optional[str]] = mapped_column("KD_KECAMATAN_ASAL", String(3))
    kd_kelurahan_asal: Mapped[Optional[str]] = mapped_column("KD_KELURAHAN_ASAL", String(3))
    kd_blok_asal: Mapped[Optional[str]] = mapped_column("KD_BLOK_ASAL", String(3))
    no_urut_asal: Mapped[Optional[str]] = mapped_column("NO_URUT_ASAL", String(4))
    kd_jns_op_asal: Mapped[Optional[str]] = mapped_column("KD_JNS_OP_ASAL", String(1))
    no_sppt_lama: Mapped[Optional[str]] = mapped_column("NO_SPPT_LAMA", String(18))
    jalan_op: Mapped[str] = mapped_column("JALAN_OP", String(30), nullable=False)
    blok_kav_no_op: Mapped[Optional[str]] = mapped_column("BLOK_KAV_NO_OP", String(15))
    kelurahan_op: Mapped[Optional[str]] = mapped_column("KELURAHAN_OP", String(30))
    rw_op: Mapped[Optional[str]] = mapped_column("RW_OP", String(2))
    rt_op: Mapped[Optional[str]] = mapped_column("RT_OP", String(3))
    kd_status_wp: Mapped[str] = mapped_column("KD_STATUS_WP", String(1), nullable=False)
    luas_bumi: Mapped[int] = mapped_column("LUAS_BUMI", BigInteger, nullable=False)
    kd_znt: Mapped[Optional[str]] = mapped_column("KD_ZNT", String(2))
    jns_bumi: Mapped[str] = mapped_column("JNS_BUMI", String(1), nullable=False)
    nilai_sistem_bumi: Mapped[int] = mapped_column("NILAI_SISTEM_BUMI", BigInteger, nullable=False, default=0)
    tgl_pendataan_op: Mapped[date] = mapped_column("TGL_PENDATAAN_OP", Date, nullable=False)
    nm_pendataan_op: Mapped[Optional[str]] = mapped_column("NM_PENDATAAN_OP", String(30))
    nip_pendata: Mapped[Optional[str]] = mapped_column("NIP_PENDATA", String(20))
    tgl_pemeriksaan_op: Mapped[date] = mapped_column("TGL_PEMERIKSAAN_OP", Date, nullable=False)
    nm_pemeriksaan_op: Mapped[Optional[str]] = mapped_column("NM_PEMERIKSAAN_OP", String(30))
    nip_pemeriksa_op: Mapped[Optional[str]] = mapped_column("NIP_PEMERIKSA_OP", String(20))
    no_persil: Mapped[Optional[str]] = mapped_column("NO_PERSIL", String(5))


class DatSubjekPajak(Base):
    __tablename__ = "dat_subjek_pajak"

    subjek_pajak_id: Mapped[str] = mapped_column("SUBJEK_PAJAK_ID", String(90), primary_key=True)
    nm_wp: Mapped[Optional[str]] = mapped_column("NM_WP", String(90))
    jalan_wp: Mapped[Optional[str]] = mapped_column("JALAN_WP", String(90))
    blok_kav_no_wp: Mapped[Optional[str]] = mapped_column("BLOK_KAV_NO_WP", String(45))
    rw_wp: Mapped[Optional[str]] = mapped_column("RW_WP", String(6))
    rt_wp: Mapped[Optional[str]] = mapped_column("RT_WP", String(9))
    kelurahan_wp: Mapped[Optional[str]] = mapped_column("KELURAHAN_WP", String(90))
    kota_wp: Mapped[Optional[str]] = mapped_column("KOTA_WP", String(90))
    kd_pos_wp: Mapped[Optional[str]] = mapped_column("KD_POS_WP", String(15))
    telp_wp: Mapped[Optional[str]] = mapped_column("TELP_WP", String(60))
    npwp: Mapped[Optional[str]] = mapped_column("NPWP", String(45))
    status_pekerjaan_wp: Mapped[Optional[str]] = mapped_column("STATUS_PEKERJAAN_WP", String(3))
    email_wp: Mapped[Optional[str]] = mapped_column("EMAIL_WP", String(150))


__all__ = [
    "Spop",
    "DatSubjekPajak",
    "RefPropinsi",
    "RefDati2",
    "RefKecamatan",
    "RefKelurahan",
]
