from typing import List

from pydantic import BaseModel


class DropdownRegion(BaseModel):
    id: int
    kode: str
    nama: str


class DropdownSimple(BaseModel):
    id: int
    nama: str


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
