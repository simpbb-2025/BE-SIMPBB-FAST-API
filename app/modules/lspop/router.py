from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import func, select

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.lspop import schemas
from app.modules.lspop.models import LampiranSpop

router = APIRouter(prefix="/lspop", tags=["lspop"])


def _to_record(row: LampiranSpop) -> schemas.LampiranRecord:
    return schemas.LampiranRecord(
        id=row.id,
        submitted_at=row.submitted_at,
        nop=row.nop,
        jumlah_bangunan=row.jumlah_bangunan,
        bangunan_ke=row.bangunan_ke,
        jenis_penggunaan_bangunan=row.jenis_penggunaan_bangunan,
        kondisi_bangunan=row.kondisi_bangunan,
        tahun_dibangun=row.tahun_dibangun,
        tahun_direnovasi=row.tahun_direnovasi,
        luas_bangunan_m2=row.luas_bangunan_m2,
        jumlah_lantai=row.jumlah_lantai,
        daya_listrik_watt=row.daya_listrik_watt,
        jenis_konstruksi=row.jenis_konstruksi,
        jenis_atap=row.jenis_atap,
        jenis_lantai=row.jenis_lantai,
        jenis_langit_langit=row.jenis_langit_langit,
        jumlah_ac=row.jumlah_ac,
        jumlah_ac_split=row.jumlah_ac_split,
        jumlah_ac_window=row.jumlah_ac_window,
        ac_sentral=row.ac_sentral,
        luas_kolam_renang_m2=row.luas_kolam_renang_m2,
        kolam_renang_diplester=row.kolam_renang_diplester,
        kolam_renang_dengan_pelapis=row.kolam_renang_dengan_pelapis,
        tenis_lampu_beton=row.tenis_lampu_beton,
        tenis_lampu_aspal=row.tenis_lampu_aspal,
        tenis_lampu_tanah_liat=row.tenis_lampu_tanah_liat,
        tenis_tanpa_lampu_beton=row.tenis_tanpa_lampu_beton,
        tenis_tanpa_lampu_aspal=row.tenis_tanpa_lampu_aspal,
        tenis_tanpa_lampu_tanah_liat=row.tenis_tanpa_lampu_tanah_liat,
        jumlah_lift_penumpang=row.jumlah_lift_penumpang,
        jumlah_lift_kapsul=row.jumlah_lift_kapsul,
        jumlah_lift_barang=row.jumlah_lift_barang,
        jumlah_tangga_berjalan_lebar_kurang_80_cm=row.jumlah_tangga_berjalan_lebar_kurang_80_cm,
        jumlah_tangga_berjalan_lebar_lebih_80_cm=row.jumlah_tangga_berjalan_lebar_lebih_80_cm,
        panjang_pagar_meter=row.panjang_pagar_meter,
        pagar_bahan_baja_besi=row.pagar_bahan_baja_besi,
        pagar_bahan_bata_batako=row.pagar_bahan_bata_batako,
        pemadam_hydrant=row.pemadam_hydrant,
        pemadam_sprinkler=row.pemadam_sprinkler,
        pemadam_fire_alarm=row.pemadam_fire_alarm,
        kedalaman_sumur_artesis_meter=row.kedalaman_sumur_artesis_meter,
        kelas_bangunan_perkantoran=row.kelas_bangunan_perkantoran,
        kelas_bangunan_ruko=row.kelas_bangunan_ruko,
        kelas_bangunan_rumah_sakit=row.kelas_bangunan_rumah_sakit,
        luas_ruang_kamar_ac_sentral_m2=row.luas_ruang_kamar_ac_sentral_m2,
        luas_ruang_lain_ac_sentral_m2=row.luas_ruang_lain_ac_sentral_m2,
        kelas_bangunan_olahraga=row.kelas_bangunan_olahraga,
        jenis_hotel=row.jenis_hotel,
        bintang_hotel=row.bintang_hotel,
        jumlah_kamar_hotel=row.jumlah_kamar_hotel,
        luas_ruang_kamar_hotel_ac_sentral_m2=row.luas_ruang_kamar_hotel_ac_sentral_m2,
        luas_ruang_lain_hotel_ac_sentral_m2=row.luas_ruang_lain_hotel_ac_sentral_m2,
        kelas_bangunan_parkir=row.kelas_bangunan_parkir,
        kelas_bangunan_apartemen=row.kelas_bangunan_apartemen,
        jumlah_kamar_apartemen=row.jumlah_kamar_apartemen,
        letak_tangki_minyak=row.letak_tangki_minyak,
        kapasitas_tangki_minyak_liter=row.kapasitas_tangki_minyak_liter,
        kelas_bangunan_sekolah=row.kelas_bangunan_sekolah,
        foto_objek_pajak=row.foto_objek_pajak,
    )


async def _load_payload(request: Request, model_cls):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    for key in ("_method", "_put", "_patch"):
        data.pop(key, None)
    return model_cls(**data)


@router.post("", response_model=schemas.LampiranResponse, status_code=status.HTTP_201_CREATED)
async def create_lspop(
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranResponse:
    payload = await _load_payload(request, schemas.LampiranCreatePayload)
    entity = LampiranSpop(id=uuid4().hex)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(entity, key, value)

    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    record = _to_record(entity)
    return schemas.LampiranResponse(message="Lampiran SPOP berhasil dibuat", data=record)


@router.get("", response_model=schemas.LampiranListResponse)
@router.get("/", response_model=schemas.LampiranListResponse, include_in_schema=False)
async def list_lspop(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    nop: Optional[str] = Query(None, max_length=50),
) -> schemas.LampiranListResponse:
    stmt = select(LampiranSpop).order_by(LampiranSpop.submitted_at.desc())
    count_stmt = select(func.count()).select_from(LampiranSpop)

    if nop:
        stmt = stmt.where(LampiranSpop.nop == nop)
        count_stmt = count_stmt.where(LampiranSpop.nop == nop)

    total = (await session.execute(count_stmt)).scalar_one()
    offset = (page - 1) * limit
    result = await session.execute(stmt.offset(offset).limit(limit))
    rows = result.scalars().all()

    data: List[schemas.LampiranRecord] = [_to_record(row) for row in rows]
    pages = (total + limit - 1) // limit if total else 0
    meta = schemas.Pagination(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=page < pages if pages else False,
        has_prev=page > 1,
    )
    return schemas.LampiranListResponse(message="Daftar lampiran SPOP berhasil diambil", data=data, meta=meta)


@router.get("/{lampiran_id}", response_model=schemas.LampiranResponse)
async def get_lspop(
    lampiran_id: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranResponse:
    entity = await session.get(LampiranSpop, lampiran_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lampiran tidak ditemukan")
    record = _to_record(entity)
    return schemas.LampiranResponse(message="Detail lampiran SPOP berhasil diambil", data=record)


@router.patch("/{lampiran_id}", response_model=schemas.LampiranResponse)
@router.put("/{lampiran_id}", response_model=schemas.LampiranResponse, include_in_schema=False)
@router.post("/{lampiran_id}", response_model=schemas.LampiranResponse, include_in_schema=False)
async def update_lspop(
    lampiran_id: str,
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranResponse:
    entity = await session.get(LampiranSpop, lampiran_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lampiran tidak ditemukan")

    payload = await _load_payload(request, schemas.LampiranUpdatePayload)
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(entity, key, value)

    await session.commit()
    await session.refresh(entity)
    record = _to_record(entity)
    return schemas.LampiranResponse(message="Lampiran SPOP berhasil diperbarui", data=record)


@router.delete("/{lampiran_id}", response_model=schemas.LampiranDeleteResponse)
async def delete_lspop(
    lampiran_id: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranDeleteResponse:
    entity = await session.get(LampiranSpop, lampiran_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lampiran tidak ditemukan")

    await session.delete(entity)
    await session.commit()
    return schemas.LampiranDeleteResponse(message="Lampiran SPOP berhasil dihapus")
