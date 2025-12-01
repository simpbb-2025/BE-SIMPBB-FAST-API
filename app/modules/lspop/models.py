from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from sqlalchemy import func


class LampiranSpop(Base):
    __tablename__ = "lampiran_spop"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    spop_id: Mapped[Optional[str]] = mapped_column(String(32))

    # Bagian Atas
    nop: Mapped[Optional[str]] = mapped_column(String(50))
    jumlah_bangunan: Mapped[Optional[int]] = mapped_column(Integer)
    bangunan_ke: Mapped[Optional[int]] = mapped_column(Integer)

    # Rincian Data Bangunan
    jenis_penggunaan_bangunan: Mapped[Optional[int]] = mapped_column(Integer)
    kondisi_bangunan: Mapped[Optional[int]] = mapped_column(Integer)
    tahun_dibangun: Mapped[Optional[int]] = mapped_column(Integer)
    tahun_direnovasi: Mapped[Optional[int]] = mapped_column(Integer)
    luas_bangunan_m2: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_lantai: Mapped[Optional[int]] = mapped_column(Integer)
    daya_listrik_watt: Mapped[Optional[int]] = mapped_column(Integer)

    # Konstruksi
    jenis_konstruksi: Mapped[Optional[int]] = mapped_column(Integer)
    jenis_atap: Mapped[Optional[int]] = mapped_column(Integer)
    jenis_lantai: Mapped[Optional[int]] = mapped_column(Integer)
    jenis_langit_langit: Mapped[Optional[int]] = mapped_column(Integer)

    # Fasilitas AC
    jumlah_ac: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_ac_split: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_ac_window: Mapped[Optional[int]] = mapped_column(Integer)
    ac_sentral: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Kolam Renang
    luas_kolam_renang_m2: Mapped[Optional[int]] = mapped_column(Integer)
    kolam_renang_diplester: Mapped[Optional[bool]] = mapped_column(Boolean)
    kolam_renang_dengan_pelapis: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Lapangan Tenis
    tenis_lampu_beton: Mapped[Optional[int]] = mapped_column(Integer)
    tenis_lampu_aspal: Mapped[Optional[int]] = mapped_column(Integer)
    tenis_lampu_tanah_liat: Mapped[Optional[int]] = mapped_column(Integer)

    tenis_tanpa_lampu_beton: Mapped[Optional[int]] = mapped_column(Integer)
    tenis_tanpa_lampu_aspal: Mapped[Optional[int]] = mapped_column(Integer)
    tenis_tanpa_lampu_tanah_liat: Mapped[Optional[int]] = mapped_column(Integer)

    # Lift
    jumlah_lift_penumpang: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_lift_kapsul: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_lift_barang: Mapped[Optional[int]] = mapped_column(Integer)

    # Tangga Berjalan
    jumlah_tangga_berjalan_lebar_kurang_80_cm: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_tangga_berjalan_lebar_lebih_80_cm: Mapped[Optional[int]] = mapped_column(Integer)

    # Pagar
    panjang_pagar_meter: Mapped[Optional[int]] = mapped_column(Integer)
    pagar_bahan_baja_besi: Mapped[Optional[bool]] = mapped_column(Boolean)
    pagar_bahan_bata_batako: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Pemadam Kebakaran
    pemadam_hydrant: Mapped[Optional[bool]] = mapped_column(Boolean)
    pemadam_sprinkler: Mapped[Optional[bool]] = mapped_column(Boolean)
    pemadam_fire_alarm: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Sumur Artesis
    kedalaman_sumur_artesis_meter: Mapped[Optional[int]] = mapped_column(Integer)

    # Perkantoran / Gedung Pemerintah (JPB 2/9)
    kelas_bangunan_perkantoran: Mapped[Optional[int]] = mapped_column(Integer)

    # Toko / Apotik / Pasar / Ruko (JPB 4)
    kelas_bangunan_ruko: Mapped[Optional[int]] = mapped_column(Integer)

    # Rumah Sakit / Klinik (JPB 6)
    kelas_bangunan_rumah_sakit: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_kamar_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_lain_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)

    # Olahraga / Rekreasi (JPB 6)
    kelas_bangunan_olahraga: Mapped[Optional[int]] = mapped_column(Integer)

    # Hotel (JPB 6)
    jenis_hotel: Mapped[Optional[int]] = mapped_column(Integer)
    bintang_hotel: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_kamar_hotel: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_kamar_hotel_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_lain_hotel_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)

    # Bangunan Parkir (JPB 12)
    kelas_bangunan_parkir: Mapped[Optional[int]] = mapped_column(Integer)

    # Apartemen (JPB 13)
    kelas_bangunan_apartemen: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_kamar_apartemen: Mapped[Optional[int]] = mapped_column(Integer)

    # Tangki Minyak (JPB 15)
    letak_tangki_minyak: Mapped[Optional[int]] = mapped_column(Integer)
    kapasitas_tangki_minyak_liter: Mapped[Optional[int]] = mapped_column(Integer)

    # Gedung Sekolah (JPB 16)
    kelas_bangunan_sekolah: Mapped[Optional[int]] = mapped_column(Integer)

    # Berkas
    foto_objek_pajak: Mapped[Optional[str]] = mapped_column(String(255))

    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


# Reference tables for relational fields (id, nama)
class RefJenisPenggunaanBangunan(Base):
    __tablename__ = "jenis_penggunaan_bangunan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKondisiBangunan(Base):
    __tablename__ = "kondisi_bangunan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefJenisKonstruksi(Base):
    __tablename__ = "jenis_konstruksi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefJenisAtap(Base):
    __tablename__ = "jenis_atap"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefJenisLantai(Base):
    __tablename__ = "jenis_lantai"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefJenisLangitLangit(Base):
    __tablename__ = "jenis_langit_langit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanPerkantoran(Base):
    __tablename__ = "kelas_bangunan_perkantoran"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanRuko(Base):
    __tablename__ = "kelas_bangunan_ruko"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanRumahSakit(Base):
    __tablename__ = "kelas_bangunan_rumah_sakit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanOlahraga(Base):
    __tablename__ = "kelas_bangunan_olahraga"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefJenisHotel(Base):
    __tablename__ = "jenis_hotel"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefBintangHotel(Base):
    __tablename__ = "bintang_hotel"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanParkir(Base):
    __tablename__ = "kelas_bangunan_parkir"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanApartemen(Base):
    __tablename__ = "kelas_bangunan_apartemen"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefKelasBangunanSekolah(Base):
    __tablename__ = "kelas_bangunan_sekolah"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


class RefLetakTangkiMinyak(Base):
    __tablename__ = "letak_tangki_minyak"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)


__all__ = ["LampiranSpop"]
