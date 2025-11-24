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

    # Bagian Atas
    nop: Mapped[Optional[str]] = mapped_column(String(50))
    jumlah_bangunan: Mapped[Optional[int]] = mapped_column(Integer)
    bangunan_ke: Mapped[Optional[int]] = mapped_column(Integer)

    # Rincian Data Bangunan
    jenis_penggunaan_bangunan: Mapped[Optional[str]] = mapped_column(String(100))
    kondisi_bangunan: Mapped[Optional[str]] = mapped_column(String(100))
    tahun_dibangun: Mapped[Optional[int]] = mapped_column(Integer)
    tahun_direnovasi: Mapped[Optional[int]] = mapped_column(Integer)
    luas_bangunan_m2: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_lantai: Mapped[Optional[int]] = mapped_column(Integer)
    daya_listrik_watt: Mapped[Optional[int]] = mapped_column(Integer)

    # Konstruksi
    jenis_konstruksi: Mapped[Optional[str]] = mapped_column(String(100))
    jenis_atap: Mapped[Optional[str]] = mapped_column(String(100))
    jenis_lantai: Mapped[Optional[str]] = mapped_column(String(100))
    jenis_langit_langit: Mapped[Optional[str]] = mapped_column(String(100))

    # Fasilitas AC
    jumlah_ac: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_ac_split: Mapped[Optional[int]] = mapped_column(Integer)
    jumlah_ac_window: Mapped[Optional[int]] = mapped_column(Integer)
    ac_sentral: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Kolam Renang
    luas_kolam_renang_m2: Mapped[Optional[int]] = mapped_column(Integer)
    kolam_renang_diplester: Mapped[Optional[bool]] = mapped_column(Boolean)
    kolam_renang_dengan_pelapis: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Lapangan Tenis (Lampu & Tanpa Lampu)
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

    # Tangga Berjalan (Eskalator)
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
    kelas_bangunan_perkantoran: Mapped[Optional[str]] = mapped_column(String(100))

    # Toko / Apotik / Pasar / Ruko (JPB 4)
    kelas_bangunan_ruko: Mapped[Optional[str]] = mapped_column(String(100))

    # Rumah Sakit / Klinik (JPB 6)
    kelas_bangunan_rumah_sakit: Mapped[Optional[str]] = mapped_column(String(100))
    luas_ruang_kamar_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_lain_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)

    # Olahraga / Rekreasi (JPB 6)
    kelas_bangunan_olahraga: Mapped[Optional[str]] = mapped_column(String(100))

    # Hotel (JPB 6)
    jenis_hotel: Mapped[Optional[str]] = mapped_column(String(100))
    bintang_hotel: Mapped[Optional[str]] = mapped_column(String(50))
    jumlah_kamar_hotel: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_kamar_hotel_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)
    luas_ruang_lain_hotel_ac_sentral_m2: Mapped[Optional[int]] = mapped_column(Integer)

    # Bangunan Parkir (JPB 12)
    kelas_bangunan_parkir: Mapped[Optional[str]] = mapped_column(String(100))

    # Apartemen (JPB 13)
    kelas_bangunan_apartemen: Mapped[Optional[str]] = mapped_column(String(100))
    jumlah_kamar_apartemen: Mapped[Optional[int]] = mapped_column(Integer)

    # Tangki Minyak (JPB 15)
    letak_tangki_minyak: Mapped[Optional[str]] = mapped_column(String(100))
    kapasitas_tangki_minyak_liter: Mapped[Optional[int]] = mapped_column(Integer)

    # Gedung Sekolah (JPB 16)
    kelas_bangunan_sekolah: Mapped[Optional[str]] = mapped_column(String(100))

    # Berkas
    foto_objek_pajak: Mapped[Optional[str]] = mapped_column(String(255))

    # Pernyataan
    formulir_sesuai_ketentuan: Mapped[Optional[bool]] = mapped_column(Boolean)

    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


__all__ = ["LampiranSpop"]
