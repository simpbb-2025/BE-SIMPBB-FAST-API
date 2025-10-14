from __future__ import annotations

from datetime import date
from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import case, func, select

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.dashboards.models import PembayaranSppt, Sppt
from app.modules.dashboards.schemas import (
    DashboardCardsData,
    DashboardCardsResponse,
    DashboardGraphItem,
    DashboardGraphResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dataclass(slots=True)
class RegionFilter:
    kd_propinsi: Optional[str]
    kd_dati2: Optional[str]
    kd_kecamatan: Optional[str]
    kd_kelurahan: Optional[str]

    @classmethod
    def from_query(
        cls,
        kd_propinsi: Optional[str],
        kd_dati2: Optional[str],
        kd_kecamatan: Optional[str],
        kd_kelurahan: Optional[str],
    ) -> "RegionFilter":
        return cls(
            kd_propinsi=_normalize_code(kd_propinsi, 2),
            kd_dati2=_normalize_code(kd_dati2, 2),
            kd_kecamatan=_normalize_code(kd_kecamatan, 3),
            kd_kelurahan=_normalize_code(kd_kelurahan, 3),
        )


def _normalize_code(value: Optional[str], length: int) -> Optional[str]:
    if value is None:
        return None
    raw = value.strip()
    if not raw:
        return None
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits:
        return digits.zfill(length)[:length]
    trimmed = raw[:length]
    return trimmed.upper()


def _region_filters(model: type[Sppt | PembayaranSppt], region: RegionFilter) -> List:
    filters: List = []
    if region.kd_propinsi:
        filters.append(model.kd_propinsi.like(f"{region.kd_propinsi}%"))
    if region.kd_dati2:
        filters.append(model.kd_dati2.like(f"{region.kd_dati2}%"))
    if region.kd_kecamatan:
        filters.append(model.kd_kecamatan.like(f"{region.kd_kecamatan}%"))
    if region.kd_kelurahan:
        filters.append(model.kd_kelurahan.like(f"{region.kd_kelurahan}%"))
    return filters


def _ensure_year(year: int) -> str:
    if not 1000 <= year <= 9999:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Parameter year harus berupa 4 digit",
        )
    return f"{year:04d}"


@router.get("/cards", response_model=DashboardCardsResponse)
async def get_dashboard_cards(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    year: int = Query(..., description="Tahun pajak 4 digit"),
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
) -> DashboardCardsResponse:
    _ensure_year(year)
    region = RegionFilter.from_query(kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan)

    sppt_filters = [Sppt.thn_pajak_sppt == f"{year:04d}", *_region_filters(Sppt, region)]

    status_text = func.upper(func.trim(func.coalesce(Sppt.status_pembayaran_sppt, "")))
    paid_case = case(
        (status_text.in_(("1", "L", "LUNAS", "Y")), 1),
        (Sppt.status_pembayaran_sppt == 1, 1),
        else_=0,
    )

    sppt_stmt = select(
        func.count().label("total_object_count"),
        func.coalesce(func.sum(Sppt.luas_bng_sppt), 0).label("total_building_area"),
        func.coalesce(func.sum(Sppt.pbb_terhutang_sppt), 0).label("total_tax_due"),
        func.coalesce(func.sum(paid_case), 0).label("paid_count"),
    ).where(*sppt_filters)

    sppt_result = await session.execute(sppt_stmt)
    sppt_row = sppt_result.one()

    pembayaran_filters = [
        PembayaranSppt.thn_pajak_sppt == f"{year:04d}",
        *_region_filters(PembayaranSppt, region),
    ]

    pembayaran_stmt = select(
        func.coalesce(func.sum(PembayaranSppt.jml_sppt_yg_dibayar), 0).label("total_realisation")
    ).where(*pembayaran_filters)

    pembayaran_result = await session.execute(pembayaran_stmt)
    total_realisation = pembayaran_result.scalar_one()

    cards_data = DashboardCardsData.from_raw(
        total_object_count=int(sppt_row.total_object_count or 0),
        total_building_area=sppt_row.total_building_area,
        total_tax_due=sppt_row.total_tax_due,
        total_realisation=total_realisation,
        paid_count=int(sppt_row.paid_count or 0),
    )

    return DashboardCardsResponse(message="Ringkasan dashboard berhasil diambil", data=cards_data)


@router.get("/graph", response_model=DashboardGraphResponse)
async def get_dashboard_graph(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    year: int = Query(..., description="Tahun pajak 4 digit"),
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
) -> DashboardGraphResponse:
    _ensure_year(year)
    region = RegionFilter.from_query(kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan)

    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    filters = [
        PembayaranSppt.tgl_pembayaran_sppt >= start_date,
        PembayaranSppt.tgl_pembayaran_sppt < end_date,
        *_region_filters(PembayaranSppt, region),
    ]

    monthly_stmt = (
        select(
            func.month(PembayaranSppt.tgl_pembayaran_sppt).label("month"),
            func.coalesce(func.sum(PembayaranSppt.jml_sppt_yg_dibayar), 0).label("amount"),
        )
        .where(*filters)
        .group_by("month")
        .order_by("month")
    )

    monthly_result = await session.execute(monthly_stmt)
    monthly_map = {int(row.month): row.amount for row in monthly_result}

    items: List[DashboardGraphItem] = []
    for month in range(1, 13):
        amount = monthly_map.get(month, 0)
        items.append(DashboardGraphItem.from_raw(month=month, amount=amount))

    return DashboardGraphResponse(message="Data grafik realisasi berhasil diambil", items=items)
