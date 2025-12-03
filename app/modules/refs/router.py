from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.core.deps import SessionDep, CurrentUserDep
from app.modules.refs import schemas
from app.modules.spop.models import (
    RefProvinsi,
    RefKabupaten,
    RefKecamatanBaru,
    RefKelurahanBaru,
    RefKelasBumiNjop,
    RefKelasBangunanNjop,
)

router = APIRouter(prefix="/refs", tags=["referensi"])


async def _get_or_404(session: SessionDep, model, item_id: int, message: str):
    instance = await session.get(model, item_id)
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return instance


@router.get("/provinsi", response_model=schemas.ProvinsiListResponse)
async def list_provinsi(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.ProvinsiListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefProvinsi))).scalar_one()
    rows = await session.execute(select(RefProvinsi).order_by(RefProvinsi.id_provinsi).offset(offset).limit(limit))
    items = [schemas.ProvinsiOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.ProvinsiListResponse(message="Daftar provinsi berhasil diambil", items=items, meta=meta)


@router.post("/provinsi", response_model=schemas.ProvinsiDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_provinsi(
    payload: schemas.ProvinsiCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.ProvinsiDetailResponse:
    record = RefProvinsi(kode_provinsi=payload.kode_provinsi, nama_provinsi=payload.nama_provinsi)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.ProvinsiOut.model_validate(record)
    return schemas.ProvinsiDetailResponse(message="Provinsi berhasil dibuat", data=data)


@router.get("/provinsi/{prov_id}", response_model=schemas.ProvinsiDetailResponse)
async def get_provinsi(prov_id: int, session: SessionDep, current_user: CurrentUserDep) -> schemas.ProvinsiDetailResponse:
    record = await _get_or_404(session, RefProvinsi, prov_id, "Provinsi tidak ditemukan")
    data = schemas.ProvinsiOut.model_validate(record)
    return schemas.ProvinsiDetailResponse(message="Detail provinsi berhasil diambil", data=data)


@router.put("/provinsi/{prov_id}", response_model=schemas.ProvinsiDetailResponse)
async def update_provinsi(
    prov_id: int, payload: schemas.ProvinsiUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.ProvinsiDetailResponse:
    record = await _get_or_404(session, RefProvinsi, prov_id, "Provinsi tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.ProvinsiOut.model_validate(record)
    return schemas.ProvinsiDetailResponse(message="Provinsi berhasil diperbarui", data=data)


@router.delete("/provinsi/{prov_id}", response_model=schemas.BaseResponse)
async def delete_provinsi(prov_id: int, session: SessionDep, current_user: CurrentUserDep) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefProvinsi, prov_id, "Provinsi tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Provinsi berhasil dihapus")


@router.get("/kabupaten", response_model=schemas.KabupatenListResponse)
async def list_kabupaten(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.KabupatenListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefKabupaten))).scalar_one()
    rows = await session.execute(
        select(RefKabupaten).order_by(RefKabupaten.id_kabupaten).offset(offset).limit(limit)
    )
    items = [schemas.KabupatenOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.KabupatenListResponse(message="Daftar kabupaten/kota berhasil diambil", items=items, meta=meta)


@router.post("/kabupaten", response_model=schemas.KabupatenDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_kabupaten(
    payload: schemas.KabupatenCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KabupatenDetailResponse:
    record = RefKabupaten(
        id_provinsi=payload.id_provinsi,
        kode_kabupaten=payload.kode_kabupaten,
        nama_kabupaten=payload.nama_kabupaten,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.KabupatenOut.model_validate(record)
    return schemas.KabupatenDetailResponse(message="Kabupaten/kota berhasil dibuat", data=data)


@router.get("/kabupaten/{kab_id}", response_model=schemas.KabupatenDetailResponse)
async def get_kabupaten(
    kab_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KabupatenDetailResponse:
    record = await _get_or_404(session, RefKabupaten, kab_id, "Kabupaten/kota tidak ditemukan")
    data = schemas.KabupatenOut.model_validate(record)
    return schemas.KabupatenDetailResponse(message="Detail kabupaten/kota berhasil diambil", data=data)


@router.put("/kabupaten/{kab_id}", response_model=schemas.KabupatenDetailResponse)
async def update_kabupaten(
    kab_id: int, payload: schemas.KabupatenUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KabupatenDetailResponse:
    record = await _get_or_404(session, RefKabupaten, kab_id, "Kabupaten/kota tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.KabupatenOut.model_validate(record)
    return schemas.KabupatenDetailResponse(message="Kabupaten/kota berhasil diperbarui", data=data)


@router.delete("/kabupaten/{kab_id}", response_model=schemas.BaseResponse)
async def delete_kabupaten(
    kab_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefKabupaten, kab_id, "Kabupaten/kota tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Kabupaten/kota berhasil dihapus")


@router.get("/kecamatan", response_model=schemas.KecamatanListResponse)
async def list_kecamatan(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.KecamatanListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefKecamatanBaru))).scalar_one()
    rows = await session.execute(
        select(RefKecamatanBaru).order_by(RefKecamatanBaru.id_kecamatan).offset(offset).limit(limit)
    )
    items = [schemas.KecamatanOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.KecamatanListResponse(message="Daftar kecamatan berhasil diambil", items=items, meta=meta)


@router.post("/kecamatan", response_model=schemas.KecamatanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_kecamatan(
    payload: schemas.KecamatanCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KecamatanDetailResponse:
    record = RefKecamatanBaru(
        id_provinsi=payload.id_provinsi,
        id_kabupaten=payload.id_kabupaten,
        kode_kecamatan=payload.kode_kecamatan,
        nama_kecamatan=payload.nama_kecamatan,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.KecamatanOut.model_validate(record)
    return schemas.KecamatanDetailResponse(message="Kecamatan berhasil dibuat", data=data)


@router.get("/kecamatan/{kec_id}", response_model=schemas.KecamatanDetailResponse)
async def get_kecamatan(
    kec_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KecamatanDetailResponse:
    record = await _get_or_404(session, RefKecamatanBaru, kec_id, "Kecamatan tidak ditemukan")
    data = schemas.KecamatanOut.model_validate(record)
    return schemas.KecamatanDetailResponse(message="Detail kecamatan berhasil diambil", data=data)


@router.put("/kecamatan/{kec_id}", response_model=schemas.KecamatanDetailResponse)
async def update_kecamatan(
    kec_id: int, payload: schemas.KecamatanUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KecamatanDetailResponse:
    record = await _get_or_404(session, RefKecamatanBaru, kec_id, "Kecamatan tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.KecamatanOut.model_validate(record)
    return schemas.KecamatanDetailResponse(message="Kecamatan berhasil diperbarui", data=data)


@router.delete("/kecamatan/{kec_id}", response_model=schemas.BaseResponse)
async def delete_kecamatan(
    kec_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefKecamatanBaru, kec_id, "Kecamatan tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Kecamatan berhasil dihapus")


@router.get("/kelurahan", response_model=schemas.KelurahanListResponse)
async def list_kelurahan(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.KelurahanListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefKelurahanBaru))).scalar_one()
    rows = await session.execute(
        select(RefKelurahanBaru).order_by(RefKelurahanBaru.id_kelurahan).offset(offset).limit(limit)
    )
    items = [schemas.KelurahanOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.KelurahanListResponse(message="Daftar kelurahan/desa berhasil diambil", items=items, meta=meta)


@router.post("/kelurahan", response_model=schemas.KelurahanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_kelurahan(
    payload: schemas.KelurahanCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelurahanDetailResponse:
    record = RefKelurahanBaru(
        id_provinsi=payload.id_provinsi,
        id_kabupaten=payload.id_kabupaten,
        id_kecamatan=payload.id_kecamatan,
        kode_kelurahan=payload.kode_kelurahan,
        nama_kelurahan=payload.nama_kelurahan,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelurahanOut.model_validate(record)
    return schemas.KelurahanDetailResponse(message="Kelurahan/desa berhasil dibuat", data=data)


@router.get("/kelurahan/{kel_id}", response_model=schemas.KelurahanDetailResponse)
async def get_kelurahan(
    kel_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelurahanDetailResponse:
    record = await _get_or_404(session, RefKelurahanBaru, kel_id, "Kelurahan/desa tidak ditemukan")
    data = schemas.KelurahanOut.model_validate(record)
    return schemas.KelurahanDetailResponse(message="Detail kelurahan/desa berhasil diambil", data=data)


@router.put("/kelurahan/{kel_id}", response_model=schemas.KelurahanDetailResponse)
async def update_kelurahan(
    kel_id: int, payload: schemas.KelurahanUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelurahanDetailResponse:
    record = await _get_or_404(session, RefKelurahanBaru, kel_id, "Kelurahan/desa tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelurahanOut.model_validate(record)
    return schemas.KelurahanDetailResponse(message="Kelurahan/desa berhasil diperbarui", data=data)


@router.delete("/kelurahan/{kel_id}", response_model=schemas.BaseResponse)
async def delete_kelurahan(
    kel_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefKelurahanBaru, kel_id, "Kelurahan/desa tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Kelurahan/desa berhasil dihapus")


@router.get("/kelas-bumi-njop", response_model=schemas.KelasBumiListResponse)
@router.get("/kelas-bumi-njop/", response_model=schemas.KelasBumiListResponse, include_in_schema=False)
async def list_kelas_bumi(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.KelasBumiListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefKelasBumiNjop))).scalar_one()
    rows = await session.execute(
        select(RefKelasBumiNjop).order_by(RefKelasBumiNjop.id).offset(offset).limit(limit)
    )
    items = [schemas.KelasBumiOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.KelasBumiListResponse(message="Daftar kelas bumi NJOP berhasil diambil", items=items, meta=meta)


@router.post("/kelas-bumi-njop", response_model=schemas.KelasBumiDetailResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/kelas-bumi-njop/",
    response_model=schemas.KelasBumiDetailResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_kelas_bumi(
    payload: schemas.KelasBumiCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBumiDetailResponse:
    record = RefKelasBumiNjop(kelas=str(payload.kelas), njop=payload.njop)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelasBumiOut.model_validate(record)
    return schemas.KelasBumiDetailResponse(message="Kelas bumi NJOP berhasil dibuat", data=data)


@router.get("/kelas-bumi-njop/{kelas_id}", response_model=schemas.KelasBumiDetailResponse)
@router.get(
    "/kelas-bumi-njop/{kelas_id}/",
    response_model=schemas.KelasBumiDetailResponse,
    include_in_schema=False,
)
async def get_kelas_bumi(
    kelas_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBumiDetailResponse:
    record = await _get_or_404(session, RefKelasBumiNjop, kelas_id, "Kelas bumi NJOP tidak ditemukan")
    data = schemas.KelasBumiOut.model_validate(record)
    return schemas.KelasBumiDetailResponse(message="Detail kelas bumi NJOP berhasil diambil", data=data)


@router.put("/kelas-bumi-njop/{kelas_id}", response_model=schemas.KelasBumiDetailResponse)
@router.put(
    "/kelas-bumi-njop/{kelas_id}/",
    response_model=schemas.KelasBumiDetailResponse,
    include_in_schema=False,
)
async def update_kelas_bumi(
    kelas_id: int, payload: schemas.KelasBumiUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBumiDetailResponse:
    record = await _get_or_404(session, RefKelasBumiNjop, kelas_id, "Kelas bumi NJOP tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        if key == "kelas":
            value = str(value)
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelasBumiOut.model_validate(record)
    return schemas.KelasBumiDetailResponse(message="Kelas bumi NJOP berhasil diperbarui", data=data)


@router.delete("/kelas-bumi-njop/{kelas_id}", response_model=schemas.BaseResponse)
@router.delete(
    "/kelas-bumi-njop/{kelas_id}/",
    response_model=schemas.BaseResponse,
    include_in_schema=False,
)
async def delete_kelas_bumi(
    kelas_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefKelasBumiNjop, kelas_id, "Kelas bumi NJOP tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Kelas bumi NJOP berhasil dihapus")


@router.get("/kelas-bangunan-njop", response_model=schemas.KelasBangunanListResponse)
@router.get(
    "/kelas-bangunan-njop/",
    response_model=schemas.KelasBangunanListResponse,
    include_in_schema=False,
)
async def list_kelas_bangunan(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.KelasBangunanListResponse:
    offset = (page - 1) * limit
    total = (await session.execute(select(func.count()).select_from(RefKelasBangunanNjop))).scalar_one()
    rows = await session.execute(
        select(RefKelasBangunanNjop).order_by(RefKelasBangunanNjop.id).offset(offset).limit(limit)
    )
    items = [schemas.KelasBangunanOut.model_validate(row) for row in rows.scalars().all()]
    meta = schemas.Pagination.create(total=total, page=page, limit=limit)
    return schemas.KelasBangunanListResponse(message="Daftar kelas bangunan NJOP berhasil diambil", items=items, meta=meta)


@router.post(
    "/kelas-bangunan-njop",
    response_model=schemas.KelasBangunanDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/kelas-bangunan-njop/",
    response_model=schemas.KelasBangunanDetailResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_kelas_bangunan(
    payload: schemas.KelasBangunanCreate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBangunanDetailResponse:
    record = RefKelasBangunanNjop(kelas=str(payload.kelas), njop=payload.njop)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelasBangunanOut.model_validate(record)
    return schemas.KelasBangunanDetailResponse(message="Kelas bangunan NJOP berhasil dibuat", data=data)


@router.get("/kelas-bangunan-njop/{kelas_id}", response_model=schemas.KelasBangunanDetailResponse)
@router.get(
    "/kelas-bangunan-njop/{kelas_id}/",
    response_model=schemas.KelasBangunanDetailResponse,
    include_in_schema=False,
)
async def get_kelas_bangunan(
    kelas_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBangunanDetailResponse:
    record = await _get_or_404(session, RefKelasBangunanNjop, kelas_id, "Kelas bangunan NJOP tidak ditemukan")
    data = schemas.KelasBangunanOut.model_validate(record)
    return schemas.KelasBangunanDetailResponse(message="Detail kelas bangunan NJOP berhasil diambil", data=data)


@router.put("/kelas-bangunan-njop/{kelas_id}", response_model=schemas.KelasBangunanDetailResponse)
@router.put(
    "/kelas-bangunan-njop/{kelas_id}/",
    response_model=schemas.KelasBangunanDetailResponse,
    include_in_schema=False,
)
async def update_kelas_bangunan(
    kelas_id: int, payload: schemas.KelasBangunanUpdate, session: SessionDep, current_user: CurrentUserDep
) -> schemas.KelasBangunanDetailResponse:
    record = await _get_or_404(session, RefKelasBangunanNjop, kelas_id, "Kelas bangunan NJOP tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        if key == "kelas":
            value = str(value)
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    data = schemas.KelasBangunanOut.model_validate(record)
    return schemas.KelasBangunanDetailResponse(message="Kelas bangunan NJOP berhasil diperbarui", data=data)


@router.delete("/kelas-bangunan-njop/{kelas_id}", response_model=schemas.BaseResponse)
@router.delete(
    "/kelas-bangunan-njop/{kelas_id}/",
    response_model=schemas.BaseResponse,
    include_in_schema=False,
)
async def delete_kelas_bangunan(
    kelas_id: int, session: SessionDep, current_user: CurrentUserDep
) -> schemas.BaseResponse:
    record = await _get_or_404(session, RefKelasBangunanNjop, kelas_id, "Kelas bangunan NJOP tidak ditemukan")
    await session.delete(record)
    await session.commit()
    return schemas.BaseResponse(message="Kelas bangunan NJOP berhasil dihapus")
