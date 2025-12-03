from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseResponse(BaseModel):
    success: bool = True
    message: str


class ProvinsiOut(BaseModel):
    id: int = Field(alias="id_provinsi")
    kode_provinsi: int
    nama_provinsi: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProvinsiCreate(BaseModel):
    kode_provinsi: int
    nama_provinsi: str = Field(max_length=100)


class ProvinsiUpdate(BaseModel):
    kode_provinsi: Optional[int] = None
    nama_provinsi: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def ensure_changes(self) -> "ProvinsiUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class ProvinsiListResponse(BaseResponse):
    items: List[ProvinsiOut]


class ProvinsiDetailResponse(BaseResponse):
    data: ProvinsiOut


class KabupatenOut(BaseModel):
    id: int = Field(alias="id_kabupaten")
    id_provinsi: int
    kode_kabupaten: int
    nama_kabupaten: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class KabupatenCreate(BaseModel):
    id_provinsi: int
    kode_kabupaten: int
    nama_kabupaten: str = Field(max_length=100)


class KabupatenUpdate(BaseModel):
    id_provinsi: Optional[int] = None
    kode_kabupaten: Optional[int] = None
    nama_kabupaten: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def ensure_changes(self) -> "KabupatenUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class KabupatenListResponse(BaseResponse):
    items: List[KabupatenOut]


class KabupatenDetailResponse(BaseResponse):
    data: KabupatenOut


class KecamatanOut(BaseModel):
    id: int = Field(alias="id_kecamatan")
    id_provinsi: int
    id_kabupaten: int
    kode_kecamatan: int
    nama_kecamatan: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class KecamatanCreate(BaseModel):
    id_provinsi: int
    id_kabupaten: int
    kode_kecamatan: int
    nama_kecamatan: str = Field(max_length=100)


class KecamatanUpdate(BaseModel):
    id_provinsi: Optional[int] = None
    id_kabupaten: Optional[int] = None
    kode_kecamatan: Optional[int] = None
    nama_kecamatan: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def ensure_changes(self) -> "KecamatanUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class KecamatanListResponse(BaseResponse):
    items: List[KecamatanOut]


class KecamatanDetailResponse(BaseResponse):
    data: KecamatanOut


class KelurahanOut(BaseModel):
    id: int = Field(alias="id_kelurahan")
    id_provinsi: int
    id_kabupaten: int
    id_kecamatan: int
    kode_kelurahan: int
    nama_kelurahan: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class KelurahanCreate(BaseModel):
    id_provinsi: int
    id_kabupaten: int
    id_kecamatan: int
    kode_kelurahan: int
    nama_kelurahan: str = Field(max_length=120)


class KelurahanUpdate(BaseModel):
    id_provinsi: Optional[int] = None
    id_kabupaten: Optional[int] = None
    id_kecamatan: Optional[int] = None
    kode_kelurahan: Optional[int] = None
    nama_kelurahan: Optional[str] = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def ensure_changes(self) -> "KelurahanUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class KelurahanListResponse(BaseResponse):
    items: List[KelurahanOut]


class KelurahanDetailResponse(BaseResponse):
    data: KelurahanOut


class KelasBumiOut(BaseModel):
    id: int
    kelas: int
    njop: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values:
            values["kelas"] = int(values.get("kelas"))
        return values


class KelasBumiCreate(BaseModel):
    kelas: int
    njop: int

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values:
            values["kelas"] = int(values.get("kelas"))
        return values


class KelasBumiUpdate(BaseModel):
    kelas: Optional[int] = None
    njop: Optional[int] = None

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values and values["kelas"] is not None:
            values["kelas"] = int(values.get("kelas"))
        return values

    @model_validator(mode="after")
    def ensure_changes(self) -> "KelasBumiUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class KelasBumiListResponse(BaseResponse):
    items: List[KelasBumiOut]


class KelasBumiDetailResponse(BaseResponse):
    data: KelasBumiOut


class KelasBangunanOut(BaseModel):
    id: int
    kelas: int
    njop: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values:
            values["kelas"] = int(values.get("kelas"))
        return values


class KelasBangunanCreate(BaseModel):
    kelas: int
    njop: int

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values:
            values["kelas"] = int(values.get("kelas"))
        return values


class KelasBangunanUpdate(BaseModel):
    kelas: Optional[int] = None
    njop: Optional[int] = None

    @model_validator(mode="before")
    def coerce_kelas(cls, values):
        if isinstance(values, dict) and "kelas" in values and values["kelas"] is not None:
            values["kelas"] = int(values.get("kelas"))
        return values

    @model_validator(mode="after")
    def ensure_changes(self) -> "KelasBangunanUpdate":
        if not self.model_dump(exclude_unset=True, exclude_none=True):
            raise ValueError("Tidak ada data yang diperbarui")
        return self


class KelasBangunanListResponse(BaseResponse):
    items: List[KelasBangunanOut]


class KelasBangunanDetailResponse(BaseResponse):
    data: KelasBangunanOut
