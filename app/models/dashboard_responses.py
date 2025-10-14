from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class PropinsiResponse(BaseModel):
    code: str
    name: str


class Dati2Response(BaseModel):
    code: str
    name: str
    propinsi_code: str


class KecamatanResponse(BaseModel):
    code: str
    name: str
    propinsi_code: str
    dati2_code: str


class KelurahanResponse(BaseModel):
    code: str
    name: str
    propinsi_code: str
    dati2_code: str
    kecamatan_code: str


class DashboardStatsData(BaseModel):
    total_sppt: int
    total_buildings: int
    total_land_area: float
    total_building_area: float
    total_tax_value: float
    total_regions: int


class DashboardFiltersData(BaseModel):
    propinsi: List[PropinsiResponse]
    dati2: List[Dati2Response]
    kecamatan: List[KecamatanResponse]
    kelurahan: List[KelurahanResponse]
    years: List[int]


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class Meta(BaseModel):
    pagination: Pagination


class BaseResponse(BaseModel):
    status: str = "success"
    message: str


class DashboardStatsResponse(BaseResponse):
    data: DashboardStatsData


class DashboardFiltersResponse(BaseResponse):
    data: DashboardFiltersData


class SpptReportStatsData(BaseModel):
    total_records: int
    total_pbb: float
    total_realization: float
    total_tunggakan: float
    total_njop: float


class SpptReportStatsResponse(BaseModel):
    total_records: int
    total_pbb: float
    total_realization: float
    total_tunggakan: float
    total_njop: float


class YearlyDataResponse(BaseModel):
    year: int
    total_pbb: float
    total_realization: float


class SpptReportTableItem(BaseModel):
    year: int
    propinsi_code: str
    dati2_code: str
    kecamatan_code: str
    kecamatan_name: Optional[str]
    kelurahan_code: str
    kelurahan_name: Optional[str]
    lembar_pbb: int
    lembar_realisasi: float
    lembar_tunggakan: float
    luas_bumi: float
    luas_bangunan: float
    njop_bumi: float
    njop_bangunan: float
    njop_total: float
    pbb_terhutang: float
    pbb_pengurang: float
    pbb_harus_bayar: float
    realisasi: float
    tunggakan: float


class SpptReportTableResponse(BaseModel):
    items: List[SpptReportTableItem]
    total: int
    page: int
    limit: int


class SpptReportFiltersData(BaseModel):
    years: List[int]
    kecamatan: List[KecamatanResponse]
    default_year: Optional[int]


class SpptReportFiltersResponse(BaseResponse):
    data: SpptReportFiltersData


class SpptReportResponse(BaseResponse):
    data: SpptReportTableResponse
    stats: SpptReportStatsResponse
    yearly: List[YearlyDataResponse]
    filters: SpptReportFiltersData

