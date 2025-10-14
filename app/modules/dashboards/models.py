from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Sppt(Base):
    __tablename__ = "sppt"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(10), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(10), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(10), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(10), primary_key=True)
    kd_blok: Mapped[str] = mapped_column("KD_BLOK", String(10), primary_key=True)
    no_urut: Mapped[str] = mapped_column("NO_URUT", String(10), primary_key=True)
    kd_jns_op: Mapped[str] = mapped_column("KD_JNS_OP", String(2), primary_key=True)
    thn_pajak_sppt: Mapped[str] = mapped_column("THN_PAJAK_SPPT", String(4), nullable=False)
    luas_bumi_sppt: Mapped[Optional[Decimal]] = mapped_column("LUAS_BUMI_SPPT", Numeric(18, 0))
    luas_bng_sppt: Mapped[Optional[Decimal]] = mapped_column("LUAS_BNG_SPPT", Numeric(18, 0))
    pbb_terhutang_sppt: Mapped[Optional[Decimal]] = mapped_column("PBB_TERHUTANG_SPPT", Numeric(18, 2))
    status_pembayaran_sppt: Mapped[Optional[str]] = mapped_column("STATUS_PEMBAYARAN_SPPT", String(1))


class PembayaranSppt(Base):
    __tablename__ = "pembayaran_sppt"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(10), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(10), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(10), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(10), primary_key=True)
    kd_blok: Mapped[str] = mapped_column("KD_BLOK", String(10), primary_key=True)
    no_urut: Mapped[str] = mapped_column("NO_URUT", String(10), primary_key=True)
    kd_jns_op: Mapped[str] = mapped_column("KD_JNS_OP", String(2), primary_key=True)
    thn_pajak_sppt: Mapped[str] = mapped_column("THN_PAJAK_SPPT", String(4), primary_key=True)
    jml_sppt_yg_dibayar: Mapped[Optional[Decimal]] = mapped_column("JML_SPPT_YG_DIBAYAR", Numeric(18, 2))
    tgl_pembayaran_sppt: Mapped[Optional[DateTime]] = mapped_column("TGL_PEMBAYARAN_SPPT", DateTime)


class SpptReport(Base):
    __tablename__ = "sppt_report"

    thn_pajak_sppt: Mapped[str] = mapped_column("THN_PAJAK_SPPT", String(4), primary_key=True)
    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(10), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(10), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(10), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(10), primary_key=True)
    nm_kecamatan: Mapped[Optional[str]] = mapped_column("NM_KECAMATAN", String(100))
    nm_kelurahan: Mapped[Optional[str]] = mapped_column("NM_KELURAHAN", String(100))
    lembar_pbb: Mapped[Optional[int]] = mapped_column("LEMBAR_PBB", Integer)
    lembar_realisasi: Mapped[Optional[Decimal]] = mapped_column("LEMBAR_REALISASI", Numeric(23, 0))
    lembar_tunggakan: Mapped[Optional[Decimal]] = mapped_column("LEMBAR_TUNGGAKAN", Numeric(23, 0))
    luas_bumi_sppt: Mapped[Optional[Decimal]] = mapped_column("LUAS_BUMI_SPPT", Numeric(41, 0))
    luas_bng_sppt: Mapped[Optional[Decimal]] = mapped_column("LUAS_BNG_SPPT", Numeric(41, 0))
    njop_sppt: Mapped[Optional[Decimal]] = mapped_column("NJOP_SPPT", Numeric(41, 0))
    pbb_yg_harus_dibayar_sppt: Mapped[Optional[Decimal]] = mapped_column("PBB_YG_HARUS_DIBAYAR_SPPT", Numeric(41, 0))
    realisasi: Mapped[Optional[Decimal]] = mapped_column("REALISASI", Numeric(41, 0))
    tunggakan: Mapped[Optional[Decimal]] = mapped_column("TUNGGAKAN", Numeric(41, 0))


class DatOpBangunan(Base):
    __tablename__ = "dat_op_bangunan"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(10), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(10), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(10), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(10), primary_key=True)
    kd_blok: Mapped[str] = mapped_column("KD_BLOK", String(10), primary_key=True)
    no_urut: Mapped[str] = mapped_column("NO_URUT", String(10), primary_key=True)
    kd_jns_op: Mapped[str] = mapped_column("KD_JNS_OP", String(2), primary_key=True)
    no_bng: Mapped[int] = mapped_column("NO_BNG", Integer, primary_key=True)
    kd_jpb: Mapped[Optional[str]] = mapped_column("KD_JPB", String(3))
    no_formulir_lspop: Mapped[Optional[str]] = mapped_column("NO_FORMULIR_LSPOP", String(15))
    thn_dibangun_bng: Mapped[Optional[str]] = mapped_column("THN_DIBANGUN_BNG", String(4))
    thn_renovasi_bng: Mapped[Optional[str]] = mapped_column("THN_RENOVASI_BNG", String(4))
    luas_bng: Mapped[Optional[Decimal]] = mapped_column("LUAS_BNG", Numeric(18, 0))
    jml_lantai_bng: Mapped[Optional[int]] = mapped_column("JML_LANTAI_BNG", Integer)
    kondisi_bng: Mapped[Optional[str]] = mapped_column("KONDISI_BNG", String(2))
    jns_konstruksi_bng: Mapped[Optional[str]] = mapped_column("JNS_KONSTRUKSI_BNG", String(2))
    jns_atap_bng: Mapped[Optional[str]] = mapped_column("JNS_ATAP_BNG", String(2))
    kd_dinding: Mapped[Optional[str]] = mapped_column("KD_DINDING", String(2))
    kd_lantai: Mapped[Optional[str]] = mapped_column("KD_LANTAI", String(2))
    kd_langit_langit: Mapped[Optional[str]] = mapped_column("KD_LANGIT_LANGIT", String(2))
    nilai_sistem_bng: Mapped[Optional[Decimal]] = mapped_column("NILAI_SISTEM_BNG", Numeric(18, 0))
    jns_transaksi_bng: Mapped[Optional[str]] = mapped_column("JNS_TRANSAKSI_BNG", String(1))
    tgl_pendataan_bng: Mapped[Optional[date]] = mapped_column("TGL_PENDATAAN_BNG", Date)
    nip_pendata_bng: Mapped[Optional[str]] = mapped_column("NIP_PENDATA_BNG", String(30))
    tgl_pemeriksaan_bng: Mapped[Optional[date]] = mapped_column("TGL_PEMERIKSAAN_BNG", Date)
    nip_pemeriksa_bng: Mapped[Optional[str]] = mapped_column("NIP_PEMERIKSA_BNG", String(30))
    tgl_perekaman_bng: Mapped[Optional[date]] = mapped_column("TGL_PEREKAMAN_BNG", Date)
    nip_perekam_bng: Mapped[Optional[str]] = mapped_column("NIP_PEREKAM_BNG", String(30))
    tgl_kunjungan_kembali: Mapped[Optional[date]] = mapped_column("TGL_KUNJUNGAN_KEMBALI", Date)
    nilai_individu: Mapped[Optional[Decimal]] = mapped_column("NILAI_INDIVIDU", Numeric(18, 0))
    aktif: Mapped[Optional[int]] = mapped_column("AKTIF", Integer)


class RefPropinsi(Base):
    __tablename__ = "ref_propinsi"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(2), primary_key=True)
    nm_propinsi: Mapped[Optional[str]] = mapped_column("NM_PROPINSI", String(100))


class RefDati2(Base):
    __tablename__ = "ref_dati2"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(2), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(2), primary_key=True)
    nm_dati2: Mapped[Optional[str]] = mapped_column("NM_DATI2", String(100))


class RefKecamatan(Base):
    __tablename__ = "ref_kecamatan"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(2), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(2), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(3), primary_key=True)
    nm_kecamatan: Mapped[Optional[str]] = mapped_column("NM_KECAMATAN", String(100))


class RefKelurahan(Base):
    __tablename__ = "ref_kelurahan"

    kd_propinsi: Mapped[str] = mapped_column("KD_PROPINSI", String(2), primary_key=True)
    kd_dati2: Mapped[str] = mapped_column("KD_DATI2", String(2), primary_key=True)
    kd_kecamatan: Mapped[str] = mapped_column("KD_KECAMATAN", String(3), primary_key=True)
    kd_kelurahan: Mapped[str] = mapped_column("KD_KELURAHAN", String(3), primary_key=True)
    nm_kelurahan: Mapped[Optional[str]] = mapped_column("NM_KELURAHAN", String(100))
