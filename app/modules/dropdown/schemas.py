from typing import List

from pydantic import BaseModel


class DropdownRegion(BaseModel):
    id: int
    kode: str
    nama: str


class DropdownSimple(BaseModel):
    id: int
    nama: str


class DropdownBasicResponse(BaseModel):
    success: bool = True
    message: str
    provinsi_subjek: List[DropdownRegion]
    kabupaten_kota_subjek: List[DropdownRegion]
    kecamatan_subjek: List[DropdownRegion]
    kelurahan_desa_subjek: List[DropdownRegion]


class DropdownResponse(BaseModel):
    success: bool = True
    message: str
    provinsi: List[DropdownRegion]
    kabupaten_kota: List[DropdownRegion]
    kecamatan: List[DropdownRegion]
    kelurahan_desa: List[DropdownRegion]
    status_subjek: List[DropdownSimple]
    pekerjaan_subjek: List[DropdownSimple]
    jenis_tanah: List[DropdownSimple]


class LspopDropdownResponse(BaseModel):
    success: bool = True
    message: str
    jenis_penggunaan_bangunan: List[DropdownSimple]
    kondisi_bangunan: List[DropdownSimple]
    jenis_konstruksi: List[DropdownSimple]
    jenis_atap: List[DropdownSimple]
    jenis_lantai: List[DropdownSimple]
    jenis_langit_langit: List[DropdownSimple]
    kelas_bangunan_perkantoran: List[DropdownSimple]
    kelas_bangunan_ruko: List[DropdownSimple]
    kelas_bangunan_rumah_sakit: List[DropdownSimple]
    kelas_bangunan_olahraga: List[DropdownSimple]
    jenis_hotel: List[DropdownSimple]
    bintang_hotel: List[DropdownSimple]
    kelas_bangunan_parkir: List[DropdownSimple]
    kelas_bangunan_apartemen: List[DropdownSimple]
    kelas_bangunan_sekolah: List[DropdownSimple]
    letak_tangki_minyak: List[DropdownSimple]


class KelasNjopDropdownResponse(BaseModel):
    success: bool = True
    message: str
    kelas_bumi_njop: List["DropdownKelasNjop"]
    kelas_bangunan_njop: List["DropdownKelasNjop"]


class DropdownKelasNjop(BaseModel):
    id: int
    kelas: str
    njop: int
