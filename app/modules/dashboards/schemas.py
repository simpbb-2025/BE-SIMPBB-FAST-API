from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel


def _to_decimal(value: Decimal | float | int | None) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


class DashboardCardsData(BaseModel):
    total_object_count: int
    total_building_area: Decimal
    total_tax_due: Decimal
    total_realisation: Decimal
    paid_count: int
    unpaid_count: int

    @classmethod
    def from_raw(
        cls,
        *,
        total_object_count: int,
        total_building_area: Decimal | float | int | None,
        total_tax_due: Decimal | float | int | None,
        total_realisation: Decimal | float | int | None,
        paid_count: int,
    ) -> "DashboardCardsData":
        return cls(
            total_object_count=total_object_count,
            total_building_area=_to_decimal(total_building_area),
            total_tax_due=_to_decimal(total_tax_due),
            total_realisation=_to_decimal(total_realisation),
            paid_count=paid_count,
            unpaid_count=max(total_object_count - paid_count, 0),
        )


class DashboardCardsResponse(BaseModel):
    success: bool = True
    message: str
    data: DashboardCardsData


class DashboardGraphItem(BaseModel):
    month: int
    label: str
    amount: Decimal

    @classmethod
    def from_raw(cls, *, month: int, amount: Decimal | float | int | None) -> "DashboardGraphItem":
        return cls(month=month, label=f"{month:02d}", amount=_to_decimal(amount))


class DashboardGraphResponse(BaseModel):
    success: bool = True
    message: str
    items: List[DashboardGraphItem]
