from __future__ import annotations

from secrets import randbelow
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.dashboards.models import DatOpBangunan
from app.modules.lspop import schemas

router = APIRouter(prefix="/lspop", tags=["lspop"])

NOP_SEGMENTS = (
    ("kd_propinsi", 2),
    ("kd_dati2", 2),
    ("kd_kecamatan", 3),
    ("kd_kelurahan", 3),
    ("kd_blok", 3),
    ("no_urut", 4),
    ("kd_jns_op", 1),
)


def _normalize_code(value: Optional[str], length: int) -> Optional[str]:
    if value is None:
        return None
    stripped = "".join(ch for ch in value.strip() if not ch.isspace())
    if not stripped:
        return None
    digits = "".join(ch for ch in stripped if ch.isdigit())
    if digits:
        return digits.zfill(length)[:length]
    return stripped.upper()[:length]


def _parse_nop(nop: str) -> Dict[str, str]:
    digits = "".join(ch for ch in nop if ch.isdigit())
    if len(digits) != 18:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="NOP harus berisi 18 digit",
        )
    cursor = 0
    result: Dict[str, str] = {}
    for key, width in NOP_SEGMENTS:
        segment = digits[cursor : cursor + width]
        result[key] = segment
        cursor += width
    return result


def _compose_nop(components: Dict[str, str]) -> str:
    return "".join(components[key] for key, _ in NOP_SEGMENTS)


def _keys_from_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
) -> Dict[str, str]:
    values = [
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    ]
    keys: Dict[str, str] = {}
    for (key, length), value in zip(NOP_SEGMENTS, values):
        normalized = _normalize_code(value, length)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Parameter {key} tidak valid",
            )
        keys[key] = normalized
    return keys


def _extract_keys(payload: schemas.LspopCreatePayload) -> Dict[str, str]:
    if payload.nop:
        return _parse_nop(payload.nop)

    components: Dict[str, str] = {}
    for key, length in NOP_SEGMENTS:
        value = getattr(payload, key)
        normalized = _normalize_code(value, length)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Kolom {key} harus diisi",
            )
        components[key] = normalized
    return components


async def _generate_form_number(session: SessionDep, retries: int = 5) -> str:
    for _ in range(retries):
        candidate = f"{randbelow(10**11):011d}"
        stmt = select(DatOpBangunan.no_formulir_lspop).where(
            DatOpBangunan.no_formulir_lspop == candidate
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is None:
            return candidate
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Gagal membuat nomor formulir LSPOP unik",
    )


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _validate_required_fields(record: DatOpBangunan, updates: Dict[str, Any]) -> None:
    target_kd_jpb = updates.get("kd_jpb", record.kd_jpb)
    if not target_kd_jpb:
        return
    required_fields = schemas.JPB_REQUIRED_FIELDS.get(target_kd_jpb)
    if not required_fields:
        return

    missing: List[str] = []
    for field in required_fields:
        if field in updates:
            candidate = updates[field]
        else:
            candidate = getattr(record, field)
        if _is_empty(candidate):
            missing.append(field)

    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"JPB {target_kd_jpb} membutuhkan field berikut: {', '.join(missing)}",
        )


def _record_to_detail(record: DatOpBangunan) -> schemas.LspopDetail:
    return schemas.LspopDetail(
        kd_propinsi=record.kd_propinsi,
        kd_dati2=record.kd_dati2,
        kd_kecamatan=record.kd_kecamatan,
        kd_kelurahan=record.kd_kelurahan,
        kd_blok=record.kd_blok,
        no_urut=record.no_urut,
        kd_jns_op=record.kd_jns_op,
        no_bng=record.no_bng,
        kd_jpb=record.kd_jpb,
        no_formulir_lspop=record.no_formulir_lspop,
        thn_dibangun_bng=record.thn_dibangun_bng,
        thn_renovasi_bng=record.thn_renovasi_bng,
        luas_bng=record.luas_bng,
        jml_lantai_bng=record.jml_lantai_bng,
        kondisi_bng=record.kondisi_bng,
        jns_konstruksi_bng=record.jns_konstruksi_bng,
        jns_atap_bng=record.jns_atap_bng,
        kd_dinding=record.kd_dinding,
        kd_lantai=record.kd_lantai,
        kd_langit_langit=record.kd_langit_langit,
        nilai_sistem_bng=record.nilai_sistem_bng,
        jns_transaksi_bng=record.jns_transaksi_bng,
        tgl_pendataan_bng=record.tgl_pendataan_bng,
        nip_pendata_bng=record.nip_pendata_bng,
        tgl_pemeriksaan_bng=record.tgl_pemeriksaan_bng,
        nip_pemeriksa_bng=record.nip_pemeriksa_bng,
        tgl_perekaman_bng=record.tgl_perekaman_bng,
        nip_perekam_bng=record.nip_perekam_bng,
        tgl_kunjungan_kembali=record.tgl_kunjungan_kembali,
        nilai_individu=record.nilai_individu,
        aktif=bool(record.aktif),
    )


async def _fetch_lspop_or_404(
    session: SessionDep, keys: Dict[str, str], no_bng: int
) -> DatOpBangunan:
    stmt = select(DatOpBangunan).where(
        and_(
            DatOpBangunan.kd_propinsi == keys["kd_propinsi"],
            DatOpBangunan.kd_dati2 == keys["kd_dati2"],
            DatOpBangunan.kd_kecamatan == keys["kd_kecamatan"],
            DatOpBangunan.kd_kelurahan == keys["kd_kelurahan"],
            DatOpBangunan.kd_blok == keys["kd_blok"],
            DatOpBangunan.no_urut == keys["no_urut"],
            DatOpBangunan.kd_jns_op == keys["kd_jns_op"],
            DatOpBangunan.no_bng == no_bng,
        )
    )
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LSPOP tidak ditemukan"
        )
    return record


def _build_history_entries(record: DatOpBangunan) -> List[schemas.LspopHistoryEntry]:
    entries: List[schemas.LspopHistoryEntry] = []
    if record.tgl_pendataan_bng:
        entries.append(
            schemas.LspopHistoryEntry(
                aktivitas="Pendataan",
                tanggal=record.tgl_pendataan_bng,
                petugas=None,
                nip=record.nip_pendata_bng,
            )
        )
    if record.tgl_pemeriksaan_bng:
        entries.append(
            schemas.LspopHistoryEntry(
                aktivitas="Pemeriksaan",
                tanggal=record.tgl_pemeriksaan_bng,
                petugas=None,
                nip=record.nip_pemeriksa_bng,
            )
        )
    if record.tgl_perekaman_bng:
        entries.append(
            schemas.LspopHistoryEntry(
                aktivitas="Perekaman",
                tanggal=record.tgl_perekaman_bng,
                petugas=None,
                nip=record.nip_perekam_bng,
            )
        )
    if record.tgl_kunjungan_kembali:
        entries.append(
            schemas.LspopHistoryEntry(
                aktivitas="Kunjungan Kembali",
                tanggal=record.tgl_kunjungan_kembali,
                petugas=None,
                nip=None,
            )
        )
    entries.sort(key=lambda item: item.tanggal)
    return entries


@router.get("", response_model=schemas.LspopSearchResponse)
@router.get("/", response_model=schemas.LspopSearchResponse, include_in_schema=False)
async def list_lspop(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    nop: Optional[str] = Query(None),
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
    kd_blok: Optional[str] = Query(None),
    no_urut: Optional[str] = Query(None),
    kd_jns_op: Optional[str] = Query(None),
    no_bng: Optional[int] = Query(None, ge=0),
    kd_jpb: Optional[str] = Query(None),
    aktif: Optional[bool] = Query(None),
    limit: int = Query(10, ge=1, le=200),
    page: int = Query(1, ge=1),
) -> schemas.LspopSearchResponse:
    offset = (page - 1) * limit
    filters = []

    if nop:
        keys = _parse_nop(nop)
        filters.extend(
            [
                DatOpBangunan.kd_propinsi == keys["kd_propinsi"],
                DatOpBangunan.kd_dati2 == keys["kd_dati2"],
                DatOpBangunan.kd_kecamatan == keys["kd_kecamatan"],
                DatOpBangunan.kd_kelurahan == keys["kd_kelurahan"],
                DatOpBangunan.kd_blok == keys["kd_blok"],
                DatOpBangunan.no_urut == keys["no_urut"],
                DatOpBangunan.kd_jns_op == keys["kd_jns_op"],
            ]
        )
    else:
        code_filters = [
            (kd_propinsi, DatOpBangunan.kd_propinsi, 2, "like"),
            (kd_dati2, DatOpBangunan.kd_dati2, 2, "like"),
            (kd_kecamatan, DatOpBangunan.kd_kecamatan, 3, "like"),
            (kd_kelurahan, DatOpBangunan.kd_kelurahan, 3, "like"),
            (kd_blok, DatOpBangunan.kd_blok, 3, "like"),
            (no_urut, DatOpBangunan.no_urut, 4, "like"),
            (kd_jns_op, DatOpBangunan.kd_jns_op, 1, "eq"),
        ]
        for value, column, length, mode in code_filters:
            normalized = _normalize_code(value, length)
            if not normalized:
                continue
            if mode == "eq":
                filters.append(column == normalized)
            else:
                filters.append(column.like(f"{normalized}%"))

    if no_bng is not None:
        filters.append(DatOpBangunan.no_bng == no_bng)

    if kd_jpb:
        normalized_jpb = _normalize_code(kd_jpb, 3)
        if normalized_jpb:
            filters.append(DatOpBangunan.kd_jpb == normalized_jpb)

    if aktif is not None:
        filters.append(DatOpBangunan.aktif == (1 if aktif else 0))

    count_stmt = select(func.count()).select_from(DatOpBangunan)
    data_stmt = select(DatOpBangunan).order_by(
        DatOpBangunan.kd_propinsi,
        DatOpBangunan.kd_dati2,
        DatOpBangunan.kd_kecamatan,
        DatOpBangunan.kd_kelurahan,
        DatOpBangunan.kd_blok,
        DatOpBangunan.no_urut,
        DatOpBangunan.kd_jns_op,
        DatOpBangunan.no_bng,
    )

    if filters:
        combined = and_(*filters)
        count_stmt = count_stmt.where(combined)
        data_stmt = data_stmt.where(combined)

    data_stmt = data_stmt.offset(offset).limit(limit)

    total = (await session.execute(count_stmt)).scalar_one()
    records = (await session.execute(data_stmt)).scalars().all()

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    base_query_params = {
        key: value
        for key, value in {
            "nop": nop,
            "kd_propinsi": kd_propinsi,
            "kd_dati2": kd_dati2,
            "kd_kecamatan": kd_kecamatan,
            "kd_kelurahan": kd_kelurahan,
            "kd_blok": kd_blok,
            "no_urut": no_urut,
            "kd_jns_op": kd_jns_op,
            "no_bng": no_bng,
            "kd_jpb": kd_jpb,
            "aktif": int(aktif) if aktif is not None else None,
            "limit": limit,
        }.items()
        if value not in (None, "")
    }

    def build_link(target_page: int) -> Optional[str]:
        if target_page < 1 or (total_pages and target_page > total_pages):
            return None
        from urllib.parse import urlencode

        query = base_query_params.copy()
        query["page"] = target_page
        return f"/api/lspop?{urlencode(query, doseq=True)}"

    links = schemas.PaginationLinks(
        prev=build_link(page - 1),
        next=build_link(page + 1),
    )

    items: List[schemas.LspopSearchItem] = []
    for record in records:
        keys = {
            key: _normalize_code(getattr(record, key), length) or ""
            for key, length in NOP_SEGMENTS
        }
        items.append(
            schemas.LspopSearchItem(
                nop=_compose_nop(keys),
                no_bng=record.no_bng,
                kd_jpb=record.kd_jpb,
                luas_bng=record.luas_bng,
                no_formulir_lspop=record.no_formulir_lspop,
                aktif=bool(record.aktif),
                thn_dibangun_bng=record.thn_dibangun_bng,
                thn_renovasi_bng=record.thn_renovasi_bng,
            )
        )

    data = schemas.LspopSearchData(
        items=items,
        meta=schemas.PaginationMeta(
            total=total,
            limit=limit,
            page=page,
            total_pages=total_pages,
            links=links,
        ),
    )

    return schemas.LspopSearchResponse(
        message="Daftar LSPOP berhasil diambil",
        data=data,
    )


@router.post(
    "",
    response_model=schemas.LspopCreateResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/", response_model=schemas.LspopCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_lspop(
    payload: schemas.LspopCreatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopCreateResponse:
    keys = _extract_keys(payload)

    duplicate_stmt = select(DatOpBangunan).where(
        and_(
            DatOpBangunan.kd_propinsi == keys["kd_propinsi"],
            DatOpBangunan.kd_dati2 == keys["kd_dati2"],
            DatOpBangunan.kd_kecamatan == keys["kd_kecamatan"],
            DatOpBangunan.kd_kelurahan == keys["kd_kelurahan"],
            DatOpBangunan.kd_blok == keys["kd_blok"],
            DatOpBangunan.no_urut == keys["no_urut"],
            DatOpBangunan.kd_jns_op == keys["kd_jns_op"],
            DatOpBangunan.no_bng == payload.no_bng,
        )
    )
    existing = await session.execute(duplicate_stmt)
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data LSPOP untuk bangunan tersebut sudah terdaftar",
        )

    form_number = payload.no_formulir_lspop
    if form_number:
        form_number = form_number.strip()
        form_check = await session.execute(
            select(DatOpBangunan.no_formulir_lspop).where(
                DatOpBangunan.no_formulir_lspop == form_number
            )
        )
        if form_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Nomor formulir LSPOP sudah digunakan",
            )
    else:
        form_number = await _generate_form_number(session)

    record = DatOpBangunan(
        kd_propinsi=keys["kd_propinsi"],
        kd_dati2=keys["kd_dati2"],
        kd_kecamatan=keys["kd_kecamatan"],
        kd_kelurahan=keys["kd_kelurahan"],
        kd_blok=keys["kd_blok"],
        no_urut=keys["no_urut"],
        kd_jns_op=keys["kd_jns_op"],
        no_bng=payload.no_bng,
        kd_jpb=payload.kd_jpb,
        no_formulir_lspop=form_number,
        thn_dibangun_bng=payload.thn_dibangun_bng,
        thn_renovasi_bng=payload.thn_renovasi_bng,
        luas_bng=payload.luas_bng,
        jml_lantai_bng=payload.jml_lantai_bng,
        kondisi_bng=payload.kondisi_bng,
        jns_konstruksi_bng=payload.jns_konstruksi_bng,
        jns_atap_bng=payload.jns_atap_bng,
        kd_dinding=payload.kd_dinding,
        kd_lantai=payload.kd_lantai,
        kd_langit_langit=payload.kd_langit_langit,
        nilai_sistem_bng=payload.nilai_sistem_bng,
        jns_transaksi_bng=payload.jns_transaksi_bng,
        tgl_pendataan_bng=payload.tgl_pendataan_bng,
        nip_pendata_bng=payload.nip_pendata_bng,
        tgl_pemeriksaan_bng=payload.tgl_pemeriksaan_bng,
        nip_pemeriksa_bng=payload.nip_pemeriksa_bng,
        tgl_perekaman_bng=payload.tgl_perekaman_bng,
        nip_perekam_bng=payload.nip_perekam_bng,
        tgl_kunjungan_kembali=payload.tgl_kunjungan_kembali,
        nilai_individu=payload.nilai_individu,
        aktif=1 if payload.aktif else 0,
    )

    session.add(record)
    await session.commit()
    await session.refresh(record)

    detail = _record_to_detail(record)
    return schemas.LspopCreateResponse(message="LSPOP berhasil ditambahkan", data=detail)


@router.get(
    "/nop/{nop}/bangunan/{no_bng}",
    response_model=schemas.LspopDetailResponse,
)
async def get_lspop_by_nop(
    nop: str,
    no_bng: int,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopDetailResponse:
    keys = _parse_nop(nop)
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    detail = _record_to_detail(record)
    return schemas.LspopDetailResponse(
        message="Detail LSPOP berhasil diambil",
        data=detail,
    )


async def _update_lspop_record(
    session: SessionDep,
    record: DatOpBangunan,
    payload: schemas.LspopUpdatePayload,
) -> schemas.LspopDetail:
    updates = payload.model_dump(exclude_unset=True)
    _validate_required_fields(record, updates)

    if "kd_jpb" in updates:
        record.kd_jpb = updates["kd_jpb"]

    if "no_formulir_lspop" in updates:
        new_form_number = updates["no_formulir_lspop"]
        if new_form_number:
            new_form_number = new_form_number.strip()
            if new_form_number != record.no_formulir_lspop:
                duplicate_check = await session.execute(
                    select(DatOpBangunan.no_formulir_lspop).where(
                        DatOpBangunan.no_formulir_lspop == new_form_number
                    )
                )
                if duplicate_check.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Nomor formulir LSPOP sudah digunakan",
                    )
            record.no_formulir_lspop = new_form_number
        else:
            record.no_formulir_lspop = await _generate_form_number(session)

    assignable_fields = [
        "thn_dibangun_bng",
        "thn_renovasi_bng",
        "luas_bng",
        "jml_lantai_bng",
        "kondisi_bng",
        "jns_konstruksi_bng",
        "jns_atap_bng",
        "kd_dinding",
        "kd_lantai",
        "kd_langit_langit",
        "nilai_sistem_bng",
        "jns_transaksi_bng",
        "tgl_pendataan_bng",
        "nip_pendata_bng",
        "tgl_pemeriksaan_bng",
        "nip_pemeriksa_bng",
        "tgl_perekaman_bng",
        "nip_perekam_bng",
        "tgl_kunjungan_kembali",
        "nilai_individu",
    ]

    for field in assignable_fields:
        if field in updates:
            setattr(record, field, updates[field])

    if "aktif" in updates:
        record.aktif = 1 if updates["aktif"] else 0

    await session.commit()
    await session.refresh(record)
    return _record_to_detail(record)


@router.put(
    "/{kd_propinsi}/{kd_dati2}/{kd_kecamatan}/{kd_kelurahan}/{kd_blok}/{no_urut}/{kd_jns_op}/{no_bng}",
    response_model=schemas.LspopDetailResponse,
)
async def update_lspop_by_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
    no_bng: int,
    payload: schemas.LspopUpdatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopDetailResponse:
    keys = _keys_from_components(
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    )
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    detail = await _update_lspop_record(session, record, payload)
    return schemas.LspopDetailResponse(
        message="LSPOP berhasil diperbarui",
        data=detail,
    )


@router.put(
    "/nop/{nop}/bangunan/{no_bng}",
    response_model=schemas.LspopDetailResponse,
)
async def update_lspop_by_nop(
    nop: str,
    no_bng: int,
    payload: schemas.LspopUpdatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopDetailResponse:
    keys = _parse_nop(nop)
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    detail = await _update_lspop_record(session, record, payload)
    return schemas.LspopDetailResponse(
        message="LSPOP berhasil diperbarui",
        data=detail,
    )


@router.delete(
    "/{kd_propinsi}/{kd_dati2}/{kd_kecamatan}/{kd_kelurahan}/{kd_blok}/{no_urut}/{kd_jns_op}/{no_bng}",
    response_model=schemas.LspopDeleteResponse,
)
async def delete_lspop_by_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
    no_bng: int,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopDeleteResponse:
    keys = _keys_from_components(
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    )
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    await session.delete(record)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LSPOP tidak dapat dihapus karena masih terhubung dengan data lain",
        )
    return schemas.LspopDeleteResponse(message="LSPOP berhasil dihapus")


@router.delete(
    "/nop/{nop}/bangunan/{no_bng}",
    response_model=schemas.LspopDeleteResponse,
)
async def delete_lspop_by_nop(
    nop: str,
    no_bng: int,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LspopDeleteResponse:
    keys = _parse_nop(nop)
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    await session.delete(record)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LSPOP tidak dapat dihapus karena masih terhubung dengan data lain",
        )
    return schemas.LspopDeleteResponse(message="LSPOP berhasil dihapus")


@router.get("/riwayat", response_model=schemas.LspopHistoryResponse)
async def get_lspop_history(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    nop: Optional[str] = Query(None),
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
    kd_blok: Optional[str] = Query(None),
    no_urut: Optional[str] = Query(None),
    kd_jns_op: Optional[str] = Query(None),
    no_bng: Optional[int] = Query(None, ge=0),
) -> schemas.LspopHistoryResponse:
    if nop:
        if no_bng is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Parameter no_bng wajib diisi ketika menggunakan NOP",
            )
        keys = _parse_nop(nop)
    else:
        if None in (
            kd_propinsi,
            kd_dati2,
            kd_kecamatan,
            kd_kelurahan,
            kd_blok,
            no_urut,
            kd_jns_op,
            no_bng,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Lengkapi parameter komponen NOP dan no_bng",
            )
        keys = _keys_from_components(
            kd_propinsi,
            kd_dati2,
            kd_kecamatan,
            kd_kelurahan,
            kd_blok,
            no_urut,
            kd_jns_op,
        )

    assert no_bng is not None
    record = await _fetch_lspop_or_404(session, keys, no_bng)
    entries = _build_history_entries(record)
    return schemas.LspopHistoryResponse(
        message="Riwayat LSPOP berhasil diambil",
        items=entries,
    )


@router.get("/riwayat-input", response_model=schemas.LspopInputHistoryResponse)
async def list_lspop_input_history(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
    kd_blok: Optional[str] = Query(None),
    kd_jns_op: Optional[str] = Query(None),
    kd_jpb: Optional[str] = Query(None),
    aktif: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    page: int = Query(1, ge=1),
) -> schemas.LspopInputHistoryResponse:
    offset = (page - 1) * limit
    filters = [DatOpBangunan.tgl_pendataan_bng.is_not(None)]

    code_filters = [
        (kd_propinsi, DatOpBangunan.kd_propinsi, 2, "like"),
        (kd_dati2, DatOpBangunan.kd_dati2, 2, "like"),
        (kd_kecamatan, DatOpBangunan.kd_kecamatan, 3, "like"),
        (kd_kelurahan, DatOpBangunan.kd_kelurahan, 3, "like"),
        (kd_blok, DatOpBangunan.kd_blok, 3, "like"),
        (kd_jns_op, DatOpBangunan.kd_jns_op, 1, "eq"),
    ]

    for value, column, length, mode in code_filters:
        normalized = _normalize_code(value, length)
        if not normalized:
            continue
        if mode == "eq":
            filters.append(column == normalized)
        else:
            filters.append(column.like(f"{normalized}%"))

    if kd_jpb:
        normalized_jpb = _normalize_code(kd_jpb, 3)
        if normalized_jpb:
            filters.append(DatOpBangunan.kd_jpb == normalized_jpb)

    if aktif is not None:
        filters.append(DatOpBangunan.aktif == (1 if aktif else 0))

    history_stmt = (
        select(DatOpBangunan)
        .where(and_(*filters))
        .order_by(
            DatOpBangunan.tgl_pendataan_bng.desc(),
            DatOpBangunan.kd_propinsi,
            DatOpBangunan.kd_dati2,
            DatOpBangunan.kd_kecamatan,
            DatOpBangunan.kd_kelurahan,
            DatOpBangunan.kd_blok,
            DatOpBangunan.no_urut,
            DatOpBangunan.kd_jns_op,
            DatOpBangunan.no_bng,
        )
        .offset(offset)
        .limit(limit)
    )

    records = (await session.execute(history_stmt)).scalars().all()

    items: List[schemas.LspopInputHistoryItem] = []
    for record in records:
        if not record.tgl_pendataan_bng:
            continue
        keys = {
            key: _normalize_code(getattr(record, key), length) or ""
            for key, length in NOP_SEGMENTS
        }
        items.append(
            schemas.LspopInputHistoryItem(
                nop=_compose_nop(keys),
                no_bng=record.no_bng,
                tanggal=record.tgl_pendataan_bng,
                petugas=None,
                nip=record.nip_pendata_bng,
            )
        )

    return schemas.LspopInputHistoryResponse(
        message="Riwayat input LSPOP berhasil diambil",
        items=items,
    )
