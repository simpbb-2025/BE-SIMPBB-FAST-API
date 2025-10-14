from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    status: str = "success"
    message: str


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class Meta(BaseModel):
    pagination: Pagination


class VerificationRequest(BaseModel):
    nop: str = Field(min_length=18, max_length=25)
    subjek_pajak_id: Optional[str] = None


class SubjekPajakResponse(BaseModel):
    subjek_pajak_id: str
    nama: Optional[str]
    alamat: Optional[str]
    kelurahan: Optional[str]
    kota: Optional[str]
    kode_pos: Optional[str]
    telepon: Optional[str]
    npwp: Optional[str]
    email: Optional[str]


class SpopResponse(BaseModel):
    nop: str
    subjek_pajak_id: Optional[str]
    jalan: Optional[str]
    blok: Optional[str]
    kelurahan: Optional[str]
    rw: Optional[str]
    rt: Optional[str]
    status_wp: Optional[str]
    luas_bumi: float
    kd_znt: Optional[str]
    jenis_bumi: Optional[str]


class VerificationData(BaseModel):
    spop: SpopResponse
    subjek_pajak: Optional[SubjekPajakResponse]


class VerificationResponse(BaseResponse):
    data: VerificationData


class SpopListResponse(BaseResponse):
    data: List[SpopResponse]
    meta: Meta


class YearsRequest(BaseModel):
    nop: str = Field(min_length=18, max_length=25)


class YearsResponse(BaseResponse):
    data: List[int]


class SpptDetail(BaseModel):
    year: int
    nop: str
    luas_bumi: float
    luas_bangunan: float
    pbb_terhutang: float
    pbb_harus_bayar: float


class SpptDetailResponse(BaseResponse):
    data: SpptDetail


class SpptBatchResponse(BaseResponse):
    data: List[SpptDetail]
