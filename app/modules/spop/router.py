from __future__ import annotations

from secrets import randbelow
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.spop import schemas
from app.modules.spop.models import (
    DatSubjekPajak,
    RefDati2,
    RefKecamatan,
    RefKelurahan,
    RefPropinsi,
    Spop,
    SpopRegistration,
)

router = APIRouter(prefix="/spop", tags=["spop"])


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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="NOP tidak valid")
    cursor = 0
    result: Dict[str, str] = {}
    for key, width in NOP_SEGMENTS:
        segment = digits[cursor : cursor + width]
        result[key] = segment
        cursor += width
    return result


def _compose_nop(fields: Dict[str, str]) -> str:
    return "".join(fields[key] for key, _ in NOP_SEGMENTS)


def _keys_from_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
) -> Dict[str, str]:
    parts = [
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    ]
    result: Dict[str, str] = {}
    for (key, length), value in zip(NOP_SEGMENTS, parts):
        normalized = _normalize_code(value, length)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Parameter {key} tidak valid",
            )
        result[key] = normalized
    return result


def _trim(expr):
    return func.trim(func.coalesce(expr, ""))


def _status_label(code: Optional[str]) -> Optional[str]:
    mapping = {
        "1": "pendaftaran",
        "2": "pemuktahiran",
        "3": "penghapusan",
    }
    if not code:
        return None
    return mapping.get(code.strip(), code.strip())


async def _generate_no_formulir(session: SessionDep, retries: int = 5) -> str:
    for _ in range(retries):
        candidate = f"{randbelow(10**11):011d}"
        stmt = select(Spop.no_formulir_spop).where(Spop.no_formulir_spop == candidate).limit(1)
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is None:
            return candidate
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal membuat nomor formulir SPOP")


async def _ensure_subjek_exists(session: SessionDep, subjek_pajak_id: str) -> None:
    stmt = select(DatSubjekPajak.subjek_pajak_id).where(
        _trim(DatSubjekPajak.subjek_pajak_id) == subjek_pajak_id.strip()
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subjek pajak tidak ditemukan")


def _registration_to_record(registration: SpopRegistration) -> schemas.RequestRecord:
    return schemas.RequestRecord(
        id=registration.id,
        submitted_at=registration.submitted_at,
        nama_awal=registration.nama_awal,
        nik_awal=registration.nik_awal,
        alamat_rumah_awal=registration.alamat_rumah_awal,
        no_telp_awal=registration.no_telp_awal,
        provinsi_op=registration.provinsi_op,
        kabupaten_op=registration.kabupaten_op,
        kecamatan_op=registration.kecamatan_op,
        kelurahan_op=registration.kelurahan_op,
        blok_op=registration.blok_op,
        no_urut_op=registration.no_urut_op,
        nama_lengkap=registration.nama_lengkap,
        nik=registration.nik,
        status_subjek=registration.status_subjek,
        pekerjaan_subjek=registration.pekerjaan_subjek,
        npwp=registration.npwp,
        no_telp_subjek=registration.no_telp_subjek,
        jalan_subjek=registration.jalan_subjek,
        blok_kav_no_subjek=registration.blok_kav_no_subjek,
        kelurahan_subjek=registration.kelurahan_subjek,
        kecamatan_subjek=registration.kecamatan_subjek,
        kabupaten_subjek=registration.kabupaten_subjek,
        provinsi_subjek=registration.provinsi_subjek,
        rt_subjek=registration.rt_subjek,
        rw_subjek=registration.rw_subjek,
        kode_pos_subjek=registration.kode_pos_subjek,
        jenis_tanah=registration.jenis_tanah,
        luas_tanah=registration.luas_tanah,
        file_ktp=registration.file_ktp,
        file_sertifikat=registration.file_sertifikat,
        file_sppt_tetangga=registration.file_sppt_tetangga,
        file_foto_objek=registration.file_foto_objek,
        file_surat_kuasa=registration.file_surat_kuasa,
        file_pendukung=registration.file_pendukung,
    )


@router.post("/requests", response_model=schemas.RequestResponse, status_code=status.HTTP_201_CREATED)
async def _load_payload(request: Request, model_cls):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    return model_cls(**data)


async def create_registration_request(
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.RequestResponse:
    payload = await _load_payload(request, schemas.RequestCreatePayload)
    registration = SpopRegistration(
        id=uuid4().hex,
        nama_awal=payload.nama_awal.strip(),
        nik_awal=payload.nik_awal.strip(),
        alamat_rumah_awal=payload.alamat_rumah_awal.strip(),
        no_telp_awal=payload.no_telp_awal.strip(),
        provinsi_op=payload.provinsi_op.strip(),
        kabupaten_op=payload.kabupaten_op.strip(),
        kecamatan_op=payload.kecamatan_op.strip(),
        kelurahan_op=payload.kelurahan_op.strip(),
        blok_op=payload.blok_op.strip(),
        no_urut_op=payload.no_urut_op.strip(),
        nama_lengkap=payload.nama_lengkap.strip(),
        nik=payload.nik.strip(),
        status_subjek=payload.status_subjek.strip(),
        pekerjaan_subjek=payload.pekerjaan_subjek.strip(),
        npwp=payload.npwp.strip() if payload.npwp else None,
        no_telp_subjek=payload.no_telp_subjek.strip(),
        jalan_subjek=payload.jalan_subjek.strip(),
        blok_kav_no_subjek=payload.blok_kav_no_subjek.strip(),
        kelurahan_subjek=payload.kelurahan_subjek.strip(),
        kecamatan_subjek=payload.kecamatan_subjek.strip(),
        kabupaten_subjek=payload.kabupaten_subjek.strip(),
        provinsi_subjek=payload.provinsi_subjek.strip(),
        rt_subjek=payload.rt_subjek.strip(),
        rw_subjek=payload.rw_subjek.strip(),
        kode_pos_subjek=payload.kode_pos_subjek.strip(),
        jenis_tanah=payload.jenis_tanah.strip(),
        luas_tanah=payload.luas_tanah,
        file_ktp=payload.file_ktp.strip(),
        file_sertifikat=payload.file_sertifikat.strip(),
        file_sppt_tetangga=payload.file_sppt_tetangga.strip(),
        file_foto_objek=payload.file_foto_objek.strip(),
        file_surat_kuasa=payload.file_surat_kuasa.strip() if payload.file_surat_kuasa else None,
        file_pendukung=payload.file_pendukung.strip() if payload.file_pendukung else None,
    )

    session.add(registration)

    await session.commit()

    await session.refresh(registration)
    record = _registration_to_record(registration)
    return schemas.RequestResponse(message="Permohonan berhasil dibuat", data=record)


@router.get("/requests", response_model=schemas.RequestListResponse)
async def list_registration_requests(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> schemas.RequestListResponse:
    stmt = select(SpopRegistration).order_by(SpopRegistration.submitted_at.desc())
    count_stmt = select(func.count()).select_from(SpopRegistration)

    total = (await session.execute(count_stmt)).scalar_one()
    offset = (page - 1) * limit
    result = await session.execute(stmt.offset(offset).limit(limit))
    rows = result.scalars().all()

    data: List[schemas.RequestRecord] = []
    for row in rows:
        data.append(_registration_to_record(row))

    pages = (total + limit - 1) // limit if total else 0
    meta = schemas.RequestPagination(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=page < pages if pages else False,
        has_prev=page > 1,
    )
    return schemas.RequestListResponse(message="Daftar permohonan berhasil diambil", data=data, meta=meta)


@router.get("/requests/{request_id}", response_model=schemas.RequestResponse)
async def get_registration_request(
    request_id: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.RequestResponse:
    registration = await session.get(SpopRegistration, request_id)
    if registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permohonan tidak ditemukan")
    record = _registration_to_record(registration)
    return schemas.RequestResponse(message="Detail permohonan berhasil diambil", data=record)


@router.patch("/requests/{request_id}", response_model=schemas.RequestResponse)
async def update_registration_request(
    request_id: str,
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.RequestResponse:
    payload = await _load_payload(request, schemas.RequestUpdatePayload)
    registration = await session.get(SpopRegistration, request_id)
    if registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permohonan tidak ditemukan")

    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(registration, key, value)

    await session.commit()
    await session.refresh(registration)
    record = _registration_to_record(registration)
    return schemas.RequestResponse(message="Permohonan berhasil diperbarui", data=record)


@router.delete("/requests/{request_id}", response_model=schemas.RequestDeleteResponse)
async def delete_registration_request(
    request_id: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.RequestDeleteResponse:
    registration = await session.get(SpopRegistration, request_id)
    if registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permohonan tidak ditemukan")
    await session.delete(registration)
    await session.commit()
    return schemas.RequestDeleteResponse(message="Permohonan berhasil dihapus")


async def _fetch_spop_detail(
    session: SessionDep,
    keys: Dict[str, str],
) -> Optional[Tuple[Spop, Optional[DatSubjekPajak], Optional[str], Optional[str], Optional[str], Optional[str]]]:
    prop_alias = aliased(RefPropinsi)
    dati2_alias = aliased(RefDati2)
    kec_alias = aliased(RefKecamatan)
    kel_alias = aliased(RefKelurahan)

    stmt = (
        select(
            Spop,
            DatSubjekPajak,
            prop_alias.nm_propinsi,
            dati2_alias.nm_dati2,
            kec_alias.nm_kecamatan,
            kel_alias.nm_kelurahan,
        )
        .outerjoin(DatSubjekPajak, _trim(DatSubjekPajak.subjek_pajak_id) == _trim(Spop.subjek_pajak_id))
        .outerjoin(prop_alias, prop_alias.kd_propinsi == func.substr(Spop.kd_propinsi, 1, 2))
        .outerjoin(
            dati2_alias,
            and_(
                dati2_alias.kd_propinsi == func.substr(Spop.kd_propinsi, 1, 2),
                dati2_alias.kd_dati2 == func.substr(Spop.kd_dati2, 1, 2),
            ),
        )
        .outerjoin(
            kec_alias,
            and_(
                kec_alias.kd_propinsi == func.substr(Spop.kd_propinsi, 1, 2),
                kec_alias.kd_dati2 == func.substr(Spop.kd_dati2, 1, 2),
                kec_alias.kd_kecamatan == func.substr(Spop.kd_kecamatan, 1, 3),
            ),
        )
        .outerjoin(
            kel_alias,
            and_(
                kel_alias.kd_propinsi == func.substr(Spop.kd_propinsi, 1, 2),
                kel_alias.kd_dati2 == func.substr(Spop.kd_dati2, 1, 2),
                kel_alias.kd_kecamatan == func.substr(Spop.kd_kecamatan, 1, 3),
                kel_alias.kd_kelurahan == func.substr(Spop.kd_kelurahan, 1, 3),
            ),
        )
        .where(
            and_(
                Spop.kd_propinsi == keys["kd_propinsi"],
                Spop.kd_dati2 == keys["kd_dati2"],
                Spop.kd_kecamatan == keys["kd_kecamatan"],
                Spop.kd_kelurahan == keys["kd_kelurahan"],
                Spop.kd_blok == keys["kd_blok"],
                Spop.no_urut == keys["no_urut"],
                Spop.kd_jns_op == keys["kd_jns_op"],
            )
        )
    )
    result = await session.execute(stmt)
    return result.one_or_none()


def _subjek_to_schema(subjek: Optional[DatSubjekPajak]) -> Optional[schemas.SubjekPajakInfo]:
    if subjek is None:
        return None
    return schemas.SubjekPajakInfo(
        subjek_pajak_id=subjek.subjek_pajak_id.strip(),
        nama=subjek.nm_wp.strip() if subjek.nm_wp else None,
        jalan=subjek.jalan_wp.strip() if subjek.jalan_wp else None,
        blok=subjek.blok_kav_no_wp.strip() if subjek.blok_kav_no_wp else None,
        rt=subjek.rt_wp.strip() if subjek.rt_wp else None,
        rw=subjek.rw_wp.strip() if subjek.rw_wp else None,
        kelurahan=subjek.kelurahan_wp.strip() if subjek.kelurahan_wp else None,
        kota=subjek.kota_wp.strip() if subjek.kota_wp else None,
        kode_pos=subjek.kd_pos_wp.strip() if subjek.kd_pos_wp else None,
        telepon=subjek.telp_wp.strip() if subjek.telp_wp else None,
        npwp=subjek.npwp.strip() if subjek.npwp else None,
        email=subjek.email_wp.strip() if subjek.email_wp else None,
    )


def _spop_to_detail(
    spop_row: Tuple[Spop, Optional[DatSubjekPajak], Optional[str], Optional[str], Optional[str], Optional[str]],
) -> schemas.SpopDetail:
    spop, subjek, nm_propinsi, nm_dati2, nm_kecamatan, nm_kelurahan = spop_row
    keys = {
        key: _normalize_code(getattr(spop, key), length) or ""
        for key, length in NOP_SEGMENTS
    }
    return schemas.SpopDetail(
        nop=_compose_nop(keys),
        kd_propinsi=keys["kd_propinsi"],
        kd_dati2=keys["kd_dati2"],
        kd_kecamatan=keys["kd_kecamatan"],
        kd_kelurahan=keys["kd_kelurahan"],
        kd_blok=keys["kd_blok"],
        no_urut=keys["no_urut"],
        kd_jns_op=keys["kd_jns_op"],
        subjek_pajak=_subjek_to_schema(subjek),
        wilayah=schemas.WilayahLabel(
            propinsi=nm_propinsi.strip() if nm_propinsi else None,
            dati2=nm_dati2.strip() if nm_dati2 else None,
            kecamatan=nm_kecamatan.strip() if nm_kecamatan else None,
            kelurahan=nm_kelurahan.strip() if nm_kelurahan else None,
        ),
        no_formulir_spop=spop.no_formulir_spop,
        jns_transaksi_op=spop.jns_transaksi_op,
        jalan_op=spop.jalan_op,
        blok_kav_no_op=spop.blok_kav_no_op,
        kelurahan_op=spop.kelurahan_op,
        rw_op=spop.rw_op,
        rt_op=spop.rt_op,
        kd_status_wp=spop.kd_status_wp,
        luas_bumi=int(spop.luas_bumi),
        kd_znt=spop.kd_znt,
        jns_bumi=spop.jns_bumi,
        nilai_sistem_bumi=int(spop.nilai_sistem_bumi),
        tgl_pendataan_op=spop.tgl_pendataan_op,
        nm_pendataan_op=spop.nm_pendataan_op,
        nip_pendata=spop.nip_pendata,
        tgl_pemeriksaan_op=spop.tgl_pemeriksaan_op,
        nm_pemeriksaan_op=spop.nm_pemeriksaan_op,
        nip_pemeriksa_op=spop.nip_pemeriksa_op,
        no_persil=spop.no_persil,
        kd_propinsi_bersama=spop.kd_propinsi_bersama,
        kd_dati2_bersama=spop.kd_dati2_bersama,
        kd_kecamatan_bersama=spop.kd_kecamatan_bersama,
        kd_kelurahan_bersama=spop.kd_kelurahan_bersama,
        kd_blok_bersama=spop.kd_blok_bersama,
        no_urut_bersama=spop.no_urut_bersama,
        kd_jns_op_bersama=spop.kd_jns_op_bersama,
        kd_propinsi_asal=spop.kd_propinsi_asal,
        kd_dati2_asal=spop.kd_dati2_asal,
        kd_kecamatan_asal=spop.kd_kecamatan_asal,
        kd_kelurahan_asal=spop.kd_kelurahan_asal,
        kd_blok_asal=spop.kd_blok_asal,
        no_urut_asal=spop.no_urut_asal,
        kd_jns_op_asal=spop.kd_jns_op_asal,
        no_sppt_lama=spop.no_sppt_lama,
    )


async def _get_detail_or_404(session: SessionDep, keys: Dict[str, str]) -> schemas.SpopDetail:
    row = await _fetch_spop_detail(session, keys)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPOP tidak ditemukan")
    return _spop_to_detail(row)


@router.get("", response_model=schemas.SpopSearchResponse)
@router.get("/", response_model=schemas.SpopSearchResponse, include_in_schema=False)
async def list_spop(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    nop: Optional[str] = Query(None),
    kd_propinsi: Optional[str] = Query(None),
    kd_dati2: Optional[str] = Query(None),
    kd_kecamatan: Optional[str] = Query(None),
    kd_kelurahan: Optional[str] = Query(None),
    kd_blok: Optional[str] = Query(None),
    kd_jns_op: Optional[str] = Query(None),
    nm_wp: Optional[str] = Query(None),
    jalan_op: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=200),
    page: int = Query(1, ge=1),
    request_url: str = Query(None, include_in_schema=False),
) -> schemas.SpopSearchResponse:
    offset = (page - 1) * limit
    filters = []
    if nop:
        keys = _parse_nop(nop)
        filters.extend(
            [
                Spop.kd_propinsi == keys["kd_propinsi"],
                Spop.kd_dati2 == keys["kd_dati2"],
                Spop.kd_kecamatan == keys["kd_kecamatan"],
                Spop.kd_kelurahan == keys["kd_kelurahan"],
                Spop.kd_blok == keys["kd_blok"],
                Spop.no_urut == keys["no_urut"],
                Spop.kd_jns_op == keys["kd_jns_op"],
            ]
        )
    else:
        code_filters = [
            (kd_propinsi, Spop.kd_propinsi, 2),
            (kd_dati2, Spop.kd_dati2, 2),
            (kd_kecamatan, Spop.kd_kecamatan, 3),
            (kd_kelurahan, Spop.kd_kelurahan, 3),
            (kd_blok, Spop.kd_blok, 3),
        ]
        for value, column, length in code_filters:
            normalized = _normalize_code(value, length)
            if normalized:
                filters.append(column.like(f"{normalized}%"))

    if kd_jns_op:
        normalized_jns = _normalize_code(kd_jns_op, 1)
        if normalized_jns:
            filters.append(Spop.kd_jns_op == normalized_jns)

    if nm_wp:
        filters.append(func.lower(_trim(DatSubjekPajak.nm_wp)).like(f"%{nm_wp.lower()}%"))
    if jalan_op:
        filters.append(func.lower(Spop.jalan_op).like(f"%{jalan_op.lower()}%"))

    join_condition = _trim(DatSubjekPajak.subjek_pajak_id) == _trim(Spop.subjek_pajak_id)

    count_stmt = select(func.count()).select_from(Spop).outerjoin(DatSubjekPajak, join_condition)
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(Spop, DatSubjekPajak.nm_wp)
        .outerjoin(DatSubjekPajak, join_condition)
        .order_by(
            Spop.kd_propinsi,
            Spop.kd_dati2,
            Spop.kd_kecamatan,
            Spop.kd_kelurahan,
            Spop.kd_blok,
            Spop.no_urut,
            Spop.kd_jns_op,
        )
        .offset(offset)
        .limit(limit)
    )
    if filters:
        stmt = stmt.where(and_(*filters))

    result = await session.execute(stmt)
    rows = result.all()

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
            "kd_jns_op": kd_jns_op,
            "nm_wp": nm_wp,
            "jalan_op": jalan_op,
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
        return f"/api/spop?{urlencode(query, doseq=True)}"

    links = schemas.PaginationLinks(
        prev=build_link(page - 1),
        next=build_link(page + 1),
    )

    items: List[schemas.SpopSearchItem] = []
    for spop, nama_wp_row in rows:
        keys = {
            key: _normalize_code(getattr(spop, key), length) or ""
            for key, length in NOP_SEGMENTS
        }
        items.append(
            schemas.SpopSearchItem(
                nop=_compose_nop(keys),
                nama_wp=nama_wp_row.strip() if nama_wp_row else None,
                jalan_op=spop.jalan_op,
                jns_transaksi_op=spop.jns_transaksi_op,
                status=_status_label(spop.jns_transaksi_op),
                no_formulir_spop=spop.no_formulir_spop,
            )
        )

    data = schemas.SpopSearchData(
        items=items,
        meta=schemas.PaginationMeta(
            total=total,
            limit=limit,
            page=page,
            total_pages=total_pages,
            links=links,
        ),
    )
    return schemas.SpopSearchResponse(message="Daftar SPOP berhasil diambil", data=data)


@router.post("", response_model=schemas.SpopMutationResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", response_model=schemas.SpopMutationResponse, status_code=status.HTTP_201_CREATED)
async def create_spop(
    payload: schemas.SpopCreatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.SpopMutationResponse:
    if payload.nop:
        keys = _parse_nop(payload.nop)
    else:
        keys = {}
        for key, length in NOP_SEGMENTS:
            normalized = _normalize_code(getattr(payload, key), length)
            if not normalized:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Kolom {key} harus diisi",
                )
            keys[key] = normalized

    existing_stmt = select(Spop).where(
        and_(
            Spop.kd_propinsi == keys["kd_propinsi"],
            Spop.kd_dati2 == keys["kd_dati2"],
            Spop.kd_kecamatan == keys["kd_kecamatan"],
            Spop.kd_kelurahan == keys["kd_kelurahan"],
            Spop.kd_blok == keys["kd_blok"],
            Spop.no_urut == keys["no_urut"],
            Spop.kd_jns_op == keys["kd_jns_op"],
        )
    )
    exists = await session.execute(existing_stmt)
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SPOP sudah terdaftar")

    await _ensure_subjek_exists(session, payload.subjek_pajak_id)

    no_formulir = await _generate_no_formulir(session)

    spop = Spop(
        kd_propinsi=keys["kd_propinsi"],
        kd_dati2=keys["kd_dati2"],
        kd_kecamatan=keys["kd_kecamatan"],
        kd_kelurahan=keys["kd_kelurahan"],
        kd_blok=keys["kd_blok"],
        no_urut=keys["no_urut"],
        kd_jns_op=keys["kd_jns_op"],
        subjek_pajak_id=payload.subjek_pajak_id.strip(),
        no_formulir_spop=no_formulir,
        jns_transaksi_op=payload.jns_transaksi_op,
        kd_propinsi_bersama=payload.kd_propinsi_bersama,
        kd_dati2_bersama=payload.kd_dati2_bersama,
        kd_kecamatan_bersama=payload.kd_kecamatan_bersama,
        kd_kelurahan_bersama=payload.kd_kelurahan_bersama,
        kd_blok_bersama=payload.kd_blok_bersama,
        no_urut_bersama=payload.no_urut_bersama,
        kd_jns_op_bersama=payload.kd_jns_op_bersama,
        kd_propinsi_asal=payload.kd_propinsi_asal,
        kd_dati2_asal=payload.kd_dati2_asal,
        kd_kecamatan_asal=payload.kd_kecamatan_asal,
        kd_kelurahan_asal=payload.kd_kelurahan_asal,
        kd_blok_asal=payload.kd_blok_asal,
        no_urut_asal=payload.no_urut_asal,
        kd_jns_op_asal=payload.kd_jns_op_asal,
        no_sppt_lama=payload.no_sppt_lama,
        jalan_op=payload.jalan_op,
        blok_kav_no_op=payload.blok_kav_no_op,
        kelurahan_op=payload.kelurahan_op,
        rw_op=payload.rw_op,
        rt_op=payload.rt_op,
        kd_status_wp=payload.kd_status_wp,
        luas_bumi=payload.luas_bumi,
        kd_znt=payload.kd_znt,
        jns_bumi=payload.jns_bumi,
        nilai_sistem_bumi=payload.nilai_sistem_bumi,
        tgl_pendataan_op=payload.tgl_pendataan_op,
        nm_pendataan_op=payload.nm_pendataan_op,
        nip_pendata=payload.nip_pendata,
        tgl_pemeriksaan_op=payload.tgl_pemeriksaan_op,
        nm_pemeriksaan_op=payload.nm_pemeriksaan_op,
        nip_pemeriksa_op=payload.nip_pemeriksa_op,
        no_persil=payload.no_persil,
    )

    session.add(spop)
    await session.commit()

    detail_row = await _fetch_spop_detail(session, keys)
    if detail_row is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal memuat data SPOP")

    detail = _spop_to_detail(detail_row)
    return schemas.SpopMutationResponse(message="SPOP berhasil ditambahkan", data=detail)


async def _update_spop(session: SessionDep, keys: Dict[str, str], payload: schemas.SpopUpdatePayload) -> schemas.SpopDetail:
    detail_row = await _fetch_spop_detail(session, keys)
    if detail_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPOP tidak ditemukan")

    spop: Spop = detail_row[0]
    if payload.subjek_pajak_id.strip() != spop.subjek_pajak_id.strip():
        await _ensure_subjek_exists(session, payload.subjek_pajak_id)
        spop.subjek_pajak_id = payload.subjek_pajak_id.strip()

    spop.jns_transaksi_op = payload.jns_transaksi_op
    spop.jalan_op = payload.jalan_op
    spop.blok_kav_no_op = payload.blok_kav_no_op
    spop.kelurahan_op = payload.kelurahan_op
    spop.rw_op = payload.rw_op
    spop.rt_op = payload.rt_op
    spop.kd_status_wp = payload.kd_status_wp
    spop.luas_bumi = payload.luas_bumi
    spop.kd_znt = payload.kd_znt
    spop.jns_bumi = payload.jns_bumi
    spop.nilai_sistem_bumi = payload.nilai_sistem_bumi
    spop.tgl_pendataan_op = payload.tgl_pendataan_op
    spop.nm_pendataan_op = payload.nm_pendataan_op
    spop.nip_pendata = payload.nip_pendata
    spop.tgl_pemeriksaan_op = payload.tgl_pemeriksaan_op
    spop.nm_pemeriksaan_op = payload.nm_pemeriksaan_op
    spop.nip_pemeriksa_op = payload.nip_pemeriksa_op
    spop.no_persil = payload.no_persil
    spop.kd_propinsi_bersama = payload.kd_propinsi_bersama
    spop.kd_dati2_bersama = payload.kd_dati2_bersama
    spop.kd_kecamatan_bersama = payload.kd_kecamatan_bersama
    spop.kd_kelurahan_bersama = payload.kd_kelurahan_bersama
    spop.kd_blok_bersama = payload.kd_blok_bersama
    spop.no_urut_bersama = payload.no_urut_bersama
    spop.kd_jns_op_bersama = payload.kd_jns_op_bersama
    spop.kd_propinsi_asal = payload.kd_propinsi_asal
    spop.kd_dati2_asal = payload.kd_dati2_asal
    spop.kd_kecamatan_asal = payload.kd_kecamatan_asal
    spop.kd_kelurahan_asal = payload.kd_kelurahan_asal
    spop.kd_blok_asal = payload.kd_blok_asal
    spop.no_urut_asal = payload.no_urut_asal
    spop.kd_jns_op_asal = payload.kd_jns_op_asal
    spop.no_sppt_lama = payload.no_sppt_lama

    await session.commit()

    refreshed = await _fetch_spop_detail(session, keys)
    return _spop_to_detail(refreshed)


@router.put(
    "/{kd_propinsi}/{kd_dati2}/{kd_kecamatan}/{kd_kelurahan}/{kd_blok}/{no_urut}/{kd_jns_op}",
    response_model=schemas.SpopMutationResponse,
)
async def update_spop_by_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
    payload: schemas.SpopUpdatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.SpopMutationResponse:
    keys = _keys_from_components(
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    )
    detail = await _update_spop(session, keys, payload)
    return schemas.SpopMutationResponse(message="SPOP berhasil diperbarui", data=detail)


@router.put("/nop/{nop}", response_model=schemas.SpopMutationResponse)
async def update_spop_by_nop(
    nop: str,
    payload: schemas.SpopUpdatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.SpopMutationResponse:
    keys = _parse_nop(nop)
    detail = await _update_spop(session, keys, payload)
    return schemas.SpopMutationResponse(message="SPOP berhasil diperbarui", data=detail)


async def _delete_spop(session: SessionDep, keys: Dict[str, str]) -> None:
    stmt = select(Spop).where(
        and_(
            Spop.kd_propinsi == keys["kd_propinsi"],
            Spop.kd_dati2 == keys["kd_dati2"],
            Spop.kd_kecamatan == keys["kd_kecamatan"],
            Spop.kd_kelurahan == keys["kd_kelurahan"],
            Spop.kd_blok == keys["kd_blok"],
            Spop.no_urut == keys["no_urut"],
            Spop.kd_jns_op == keys["kd_jns_op"],
        )
    )
    result = await session.execute(stmt)
    spop = result.scalar_one_or_none()
    if spop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPOP tidak ditemukan")

    try:
        await session.delete(spop)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SPOP tidak dapat dihapus karena masih terhubung")


@router.delete(
    "/{kd_propinsi}/{kd_dati2}/{kd_kecamatan}/{kd_kelurahan}/{kd_blok}/{no_urut}/{kd_jns_op}",
    response_model=schemas.SpopDeleteResponse,
)
async def delete_spop_by_components(
    kd_propinsi: str,
    kd_dati2: str,
    kd_kecamatan: str,
    kd_kelurahan: str,
    kd_blok: str,
    no_urut: str,
    kd_jns_op: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.SpopDeleteResponse:
    keys = _keys_from_components(
        kd_propinsi,
        kd_dati2,
        kd_kecamatan,
        kd_kelurahan,
        kd_blok,
        no_urut,
        kd_jns_op,
    )
    await _delete_spop(session, keys)
    return schemas.SpopDeleteResponse(message="SPOP berhasil dihapus")


@router.delete("/nop/{nop}", response_model=schemas.SpopDeleteResponse)
async def delete_spop_by_nop(
    nop: str,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.SpopDeleteResponse:
    keys = _parse_nop(nop)
    await _delete_spop(session, keys)
    return schemas.SpopDeleteResponse(message="SPOP berhasil dihapus")


async def _get_history(session: SessionDep, keys: Dict[str, str]) -> List[schemas.RiwayatEntry]:
    stmt = select(Spop).where(
        and_(
            Spop.kd_propinsi == keys["kd_propinsi"],
            Spop.kd_dati2 == keys["kd_dati2"],
            Spop.kd_kecamatan == keys["kd_kecamatan"],
            Spop.kd_kelurahan == keys["kd_kelurahan"],
            Spop.kd_blok == keys["kd_blok"],
            Spop.no_urut == keys["no_urut"],
            Spop.kd_jns_op == keys["kd_jns_op"],
        )
    )
    result = await session.execute(stmt)
    spop = result.scalar_one_or_none()
    if spop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPOP tidak ditemukan")

    entries: List[schemas.RiwayatEntry] = []
    if spop.tgl_pendataan_op:
        entries.append(
            schemas.RiwayatEntry(
                aktivitas="Pendataan",
                tanggal=spop.tgl_pendataan_op,
                petugas=spop.nm_pendataan_op,
                nip=spop.nip_pendata,
            )
        )
    if spop.tgl_pemeriksaan_op:
        entries.append(
            schemas.RiwayatEntry(
                aktivitas="Pemeriksaan",
                tanggal=spop.tgl_pemeriksaan_op,
                petugas=spop.nm_pemeriksaan_op,
                nip=spop.nip_pemeriksa_op,
            )
        )

    entries.sort(key=lambda item: item.tanggal)
    return entries


@router.get("/riwayat", response_model=schemas.RiwayatResponse)
async def get_spop_history(
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
) -> schemas.RiwayatResponse:
    if nop:
        keys = _parse_nop(nop)
    else:
        required = [
            kd_propinsi,
            kd_dati2,
            kd_kecamatan,
            kd_kelurahan,
            kd_blok,
            no_urut,
            kd_jns_op,
        ]
        if not all(required):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Isi parameter NOP atau lengkapkan komponen kunci",
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

    items = await _get_history(session, keys)
    return schemas.RiwayatResponse(message="Riwayat SPOP berhasil diambil", items=items)
