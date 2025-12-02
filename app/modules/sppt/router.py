from __future__ import annotations

from math import ceil
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, text
from sqlmodel import and_, or_, select

from app.auth.service import get_current_user
from app.core.deps import SessionDep
from app.modules.sppt import schemas
from app.modules.sppt.models import DatSubjekPajak, Spop, Sppt, User, OpRegistration
from uuid import uuid4

router = APIRouter(prefix="/sppt", tags=["op"])


def normalize(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed.upper() if trimmed else None


def parse_nop(nop: str) -> Dict[str, str]:
    digits = "".join(filter(str.isdigit, nop))
    if len(digits) != 18:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP tidak valid")
    return {
        "kd_propinsi": digits[0:2],
        "kd_dati2": digits[2:4],
        "kd_kecamatan": digits[4:7],
        "kd_kelurahan": digits[7:10],
        "kd_blok": digits[10:13],
        "no_urut": digits[13:17],
        "kd_jns_op": digits[17],
    }


def compose_nop(fields: Dict[str, str]) -> str:
    return (
        fields["kd_propinsi"]
        + fields["kd_dati2"]
        + fields["kd_kecamatan"]
        + fields["kd_kelurahan"]
        + fields["kd_blok"]
        + fields["no_urut"]
        + fields["kd_jns_op"]
    )


async def _fetch_spop(
    session: SessionDep,
    *,
    nop_fields: Dict[str, str],
    subjek_pajak_id: Optional[str] = None,
) -> Optional[tuple[Spop, Optional[DatSubjekPajak]]]:
    stmt = (
        select(Spop, DatSubjekPajak)
        .select_from(Spop)
        .join(DatSubjekPajak, Spop.subjek_pajak_id == DatSubjekPajak.subjek_pajak_id, isouter=True)
    )

    conditions = [
        Spop.kd_propinsi == nop_fields["kd_propinsi"],
        Spop.kd_dati2 == nop_fields["kd_dati2"],
        Spop.kd_kecamatan == nop_fields["kd_kecamatan"],
        Spop.kd_kelurahan == nop_fields["kd_kelurahan"],
        Spop.kd_blok == nop_fields["kd_blok"],
        Spop.no_urut == nop_fields["no_urut"],
        Spop.kd_jns_op == nop_fields["kd_jns_op"],
    ]

    if subjek_pajak_id:
        conditions.append(Spop.subjek_pajak_id == subjek_pajak_id)

    stmt = stmt.where(and_(*conditions))

    result = await session.execute(stmt)
    return result.first()


@router.get("", response_model=schemas.SpptAutoListResponse)
async def list_sppt_by_nop(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    nop: str = Query(..., min_length=5, max_length=32),
) -> schemas.SpptAutoListResponse:
    digits = "".join(ch for ch in (nop or "") if ch.isdigit())
    if len(digits) != 18:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP tidak valid")
    nop_norm = digits

    result = await session.execute(
        text(
            """
            SELECT s.id, s.spop_id, s.lspop_id, s.nop, s.bumi_njop, s.bangunan_njop,
                   COALESCE(s.bumi_njop,0) + COALESCE(s.bangunan_njop,0) AS total_njop,
                   s.njoptkp,
                   s.pbb_persen AS pbb_persen_id,
                   COALESCE(t.pbb_persen, 0) AS pbb_persen_value,
                   s.create_at,
                   COALESCE(sr.luas_tanah, 0) AS luas_bumi,
                   rb.id AS kelas_bumi_njop_id,
                   rb.kelas AS kelas_bumi_njop_kelas,
                   rb.njop AS kelas_bumi_njop_njop,
                   sr.kelas_bangunan_njop AS kelas_bangunan_njop_id,
                   rbn.kelas AS kelas_bangunan_njop_kelas,
                   rbn.njop AS kelas_bangunan_njop_njop,
                   COALESCE(ls.luas_bangunan_m2, 0) AS luas_bangunan
            FROM sppt s
            LEFT JOIN pbb_p2 t ON t.id = s.pbb_persen
            LEFT JOIN spop_registration sr ON sr.id = s.spop_id
            LEFT JOIN kelas_bumi_njop rb ON rb.id = sr.kelas_bumi_njop
            LEFT JOIN lampiran_spop ls ON ls.id = s.lspop_id
            LEFT JOIN kelas_bangunan_njop rbn ON rbn.id = sr.kelas_bangunan_njop
            WHERE s.nop = :nop
            ORDER BY s.create_at DESC
            """
        ),
        {"nop": nop_norm},
    )
    rows = result.mappings().all()
    items: List[schemas.SpptAutoItem] = [_sppt_auto_row_to_schema(row) for row in rows]

    total_bangunan = len(items)
    if not items:
        return schemas.SpptAutoListResponse(
            message="Data SPPT",
            data=[],
            total_bangunan=0,
            total_luas_bumi=0,
            total_luas_bangunan=0,
            total_njop=0,
            pbb_persen_id=0,
            pbb_persen=0.0,
            pbb_terhutang=0,
        )

    # Hitung summary: 1x bumi_njop + seluruh bangunan_njop
    bumi_njop = max((int(row["bumi_njop"] or 0) for row in rows), default=0)
    bangunan_sum = sum(int(row["bangunan_njop"] or 0) for row in rows)
    summary_total_njop = bumi_njop + bangunan_sum
    pbb_persen_id = int(rows[0]["pbb_persen_id"] or 0)
    pbb_persen = float(rows[0]["pbb_persen_value"] or 0)
    njoptkp = int(rows[0]["njoptkp"] or 0)
    summary_pbb_terhutang = int(max(summary_total_njop - njoptkp, 0) * pbb_persen)
    total_luas_bumi = max((int(row["luas_bumi"] or 0) for row in rows), default=0)
    total_luas_bangunan = sum(int(row["luas_bangunan"] or 0) for row in rows)

    return schemas.SpptAutoListResponse(
        message="Data SPPT",
        data=items,
        total_bangunan=total_bangunan,
        total_luas_bumi=total_luas_bumi,
        total_luas_bangunan=total_luas_bangunan,
        total_njop=summary_total_njop,
        pbb_persen_id=pbb_persen_id,
        pbb_persen=pbb_persen,
        pbb_terhutang=summary_pbb_terhutang,
    )

def _sppt_auto_row_to_schema(row) -> schemas.SpptAutoItem:
    return schemas.SpptAutoItem(
        id=str(row["id"]),
        spop_id=str(row["spop_id"]),
        lspop_id=str(row["lspop_id"]),
        nop=str(row["nop"]),
        bumi_njop=int(row["bumi_njop"] or 0),
        bangunan_njop=int(row["bangunan_njop"] or 0),
        luas_bumi=int(row["luas_bumi"] or 0),
        luas_bangunan=int(row["luas_bangunan"] or 0),
        kelas_bumi_njop=schemas.NjopClass(
            id=int(row["kelas_bumi_njop_id"]),
            kelas=str(row["kelas_bumi_njop_kelas"]),
            njop=int(row["kelas_bumi_njop_njop"]),
        )
        if row["kelas_bumi_njop_id"] is not None
        else None,
        kelas_bangunan_njop=schemas.NjopClass(
            id=int(row["kelas_bangunan_njop_id"]),
            kelas=str(row["kelas_bangunan_njop_kelas"]),
            njop=int(row["kelas_bangunan_njop_njop"]),
        )
        if row["kelas_bangunan_njop_id"] is not None
        else None,
        create_at=row["create_at"],
    )


def _spop_to_response(nop_fields: Dict[str, str], spop: Spop) -> schemas.SpopResponse:
    return schemas.SpopResponse(
        nop=compose_nop(nop_fields),
        subjek_pajak_id=spop.subjek_pajak_id,
        jalan=spop.jalan_op,
        blok=spop.blok_kav_no_op,
        kelurahan=spop.kelurahan_op,
        rw=spop.rw_op,
        rt=spop.rt_op,
        status_wp=spop.kd_status_wp,
        luas_bumi=float(spop.luas_bumi or 0),
        kd_znt=spop.kd_znt,
        jenis_bumi=spop.jns_bumi,
    )


def _subjek_to_response(subjek: DatSubjekPajak) -> schemas.SubjekPajakResponse:
    alamat_parts = [subjek.jalan_wp, subjek.blok_kav_no_wp]
    alamat = " ".join(filter(None, alamat_parts)) or None
    return schemas.SubjekPajakResponse(
        subjek_pajak_id=subjek.subjek_pajak_id,
        nama=subjek.nm_wp,
        alamat=alamat,
        kelurahan=subjek.kelurahan_wp,
        kota=subjek.kota_wp,
        kode_pos=subjek.kd_pos_wp,
        telepon=subjek.telp_wp,
        npwp=subjek.npwp,
        email=subjek.email_wp,
    )


@router.post("/verifikasi", response_model=schemas.VerificationResponse)
async def verify_spop(
    payload: schemas.VerificationRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schemas.VerificationResponse:
    nop_fields = parse_nop(payload.nop)

    result = await _fetch_spop(session, nop_fields=nop_fields, subjek_pajak_id=payload.subjek_pajak_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data SPOP tidak ditemukan")

    spop, subjek = result
    verification_data = schemas.VerificationData(
        spop=_spop_to_response(nop_fields, spop),
        subjek_pajak=_subjek_to_response(subjek) if subjek else None,
    )

    return schemas.VerificationResponse(message="Verifikasi berhasil", data=verification_data)


@router.get("/spop", response_model=schemas.SpopListResponse)
async def list_spop(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Cari berdasarkan NOP, Subjek Pajak, atau alamat"),
    sort_by: Optional[str] = Query(
        "nop",
        regex="^(nop|subjek_pajak_id|luas_bumi)$",
        description="Kolom sorting yang diizinkan",
    ),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
) -> schemas.SpopListResponse:
    offset = (page - 1) * limit

    stmt = select(Spop)
    count_stmt = select(func.count()).select_from(Spop)

    if search:
        term = f"%{normalize(search)}%"
        condition = or_(
            func.upper(
                func.concat(
                    Spop.kd_propinsi,
                    Spop.kd_dati2,
                    Spop.kd_kecamatan,
                    Spop.kd_kelurahan,
                    Spop.kd_blok,
                    Spop.no_urut,
                    Spop.kd_jns_op,
                )
            ).like(term),
            func.upper(Spop.subjek_pajak_id).like(term),
            func.upper(Spop.jalan_op).like(term),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if sort_by == "nop":
        order_columns = [
            Spop.kd_propinsi,
            Spop.kd_dati2,
            Spop.kd_kecamatan,
            Spop.kd_kelurahan,
            Spop.kd_blok,
            Spop.no_urut,
            Spop.kd_jns_op,
        ]
    elif sort_by == "subjek_pajak_id":
        order_columns = [Spop.subjek_pajak_id]
    else:
        order_columns = [Spop.luas_bumi]

    if sort_order == "desc":
        order_columns = [col.desc() for col in order_columns]

    stmt = stmt.order_by(*order_columns).offset(offset).limit(limit)

    total = (await session.execute(count_stmt)).scalar_one()
    rows = (await session.execute(stmt)).scalars().all()

    data: list[schemas.SpopResponse] = []
    for spop in rows:
        fields = {
            "kd_propinsi": spop.kd_propinsi,
            "kd_dati2": spop.kd_dati2,
            "kd_kecamatan": spop.kd_kecamatan,
            "kd_kelurahan": spop.kd_kelurahan,
            "kd_blok": spop.kd_blok,
            "no_urut": spop.no_urut,
            "kd_jns_op": spop.kd_jns_op,
        }
        data.append(_spop_to_response(fields, spop))

    pages = ceil(total / limit) if total else 0
    pagination = schemas.Pagination(
        total=int(total),
        page=page,
        limit=limit,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )

    return schemas.SpopListResponse(
        message="Data SPOP berhasil diambil",
        data=data,
        meta=schemas.Meta(pagination=pagination),
    )


@router.post("/esppt", response_model=schemas.EspptResponse)
async def cek_esppt(
    payload: schemas.EspptRequest,
    session: SessionDep,
) -> schemas.EspptResponse:
    """Public E-SPPT check by NOP + KTP (SUBJEK_PAJAK_ID).

    Returns latest SPPT data along with SPOP and subject info.
    """
    fields = parse_nop(payload.nop)

    # Fetch SPOP + subject first to validate KTP linkage
    result = await _fetch_spop(session, nop_fields=fields)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data tidak ditemukan")

    spop, subjek = result
    ktp_input = (payload.ktp or "").strip()
    spid = (spop.subjek_pajak_id or "").strip()
    if not ktp_input or (spid and spid != ktp_input):
        # Hide existence details to avoid leakage
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data tidak ditemukan")

    # Latest SPPT for the NOP
    stmt = (
        select(Sppt)
        .where(
            and_(
                Sppt.kd_propinsi == fields["kd_propinsi"],
                Sppt.kd_dati2 == fields["kd_dati2"],
                Sppt.kd_kecamatan == fields["kd_kecamatan"],
                Sppt.kd_kelurahan == fields["kd_kelurahan"],
                Sppt.kd_blok == fields["kd_blok"],
                Sppt.no_urut == fields["no_urut"],
                Sppt.kd_jns_op == fields["kd_jns_op"],
            )
        )
        .order_by(Sppt.thn_pajak_sppt.desc())
        .limit(1)
    )

    sppt_row = (await session.execute(stmt)).scalar_one_or_none()
    if sppt_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPPT tidak ditemukan")

    detail = schemas.SpptDetail(
        year=int(sppt_row.thn_pajak_sppt),
        nop=compose_nop(fields),
        luas_bumi=float(sppt_row.luas_bumi_sppt or 0),
        luas_bangunan=float(sppt_row.luas_bng_sppt or 0),
        pbb_terhutang=float(sppt_row.pbb_terhutang_sppt or 0),
        pbb_harus_bayar=float(getattr(sppt_row, "pbb_yg_harus_dibayar_sppt", 0) or 0),
    )

    data = schemas.EspptData(
        spop=_spop_to_response(fields, spop),
        subjek_pajak=_subjek_to_response(subjek) if subjek else None,
        sppt=detail,
    )

    return schemas.EspptResponse(message="Data e-SPPT", data=data)


@router.post("/op-registration", response_model=schemas.OpRegResponse)
async def submit_op_registration(
    payload: schemas.OpRegCreate,
    session: SessionDep,
) -> schemas.OpRegResponse:
    # Create a staging record. This is public; no auth enforced.
    now_fields = {}
    record = OpRegistration(
        id=uuid4().hex,
        status="submitted",
        nama_lengkap=payload.nama_lengkap,
        alamat_rumah=payload.alamat_rumah,
        telepon=payload.telepon,
        ktp=payload.ktp,
        nama_wp=payload.nama_wp,
        alamat_wp=payload.alamat_wp,
        alamat_op=payload.alamat_op,
        kd_propinsi=payload.kd_propinsi,
        kd_dati2=payload.kd_dati2,
        kd_kecamatan=payload.kd_kecamatan,
        kd_kelurahan=payload.kd_kelurahan,
        luas_bumi=payload.luas_bumi,
        luas_bangunan=payload.luas_bangunan,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    data = schemas.OpRegRead.model_validate(record, from_attributes=True)
    return schemas.OpRegResponse(message="Pengajuan pendaftaran OP diterima", data=data)


@router.get("/esppt", response_model=schemas.EspptResponse)
async def cek_esppt_params(
    session: SessionDep,
    nop: Optional[str] = Query(default=None, min_length=18, max_length=25),
    ktp: Optional[str] = Query(default=None, min_length=8, max_length=30),
) -> schemas.EspptResponse:
    """Public E-SPPT check using query params.

    - If both `nop` and `ktp` are provided: ensure they match the same record.
    - If only `nop` provided: return latest SPPT for that NOP.
    - If only `ktp` provided: find a NOP by that SUBJEK_PAJAK_ID and return its latest SPPT.
    """
    if not nop and not ktp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimal isi salah satu dari 'nop' atau 'ktp'")

    spop: Optional[Spop] = None
    subjek: Optional[DatSubjekPajak] = None
    fields: Dict[str, str]

    if nop:
        fields = parse_nop(nop)
        res = await _fetch_spop(session, nop_fields=fields)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data tidak ditemukan")
        spop, subjek = res
        if ktp:
            spid = (spop.subjek_pajak_id or "").strip()
            if not spid or spid != ktp.strip():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data tidak ditemukan")
    else:
        # Only KTP provided: pick one SPOP by SUBJEK_PAJAK_ID
        ktp_norm = ktp.strip()
        row = (
            await session.execute(
                select(Spop, DatSubjekPajak)
                .select_from(Spop)
                .join(DatSubjekPajak, Spop.subjek_pajak_id == DatSubjekPajak.subjek_pajak_id, isouter=True)
                .where(Spop.subjek_pajak_id == ktp_norm)
                .limit(1)
            )
        ).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data tidak ditemukan")
        spop, subjek = row
        fields = {
            "kd_propinsi": spop.kd_propinsi,
            "kd_dati2": spop.kd_dati2,
            "kd_kecamatan": spop.kd_kecamatan,
            "kd_kelurahan": spop.kd_kelurahan,
            "kd_blok": spop.kd_blok,
            "no_urut": spop.no_urut,
            "kd_jns_op": spop.kd_jns_op,
        }

    # Latest SPPT for the resolved fields
    stmt = (
        select(Sppt)
        .where(
            and_(
                Sppt.kd_propinsi == fields["kd_propinsi"],
                Sppt.kd_dati2 == fields["kd_dati2"],
                Sppt.kd_kecamatan == fields["kd_kecamatan"],
                Sppt.kd_kelurahan == fields["kd_kelurahan"],
                Sppt.kd_blok == fields["kd_blok"],
                Sppt.no_urut == fields["no_urut"],
                Sppt.kd_jns_op == fields["kd_jns_op"],
            )
        )
        .order_by(Sppt.thn_pajak_sppt.desc())
        .limit(1)
    )

    sppt_row = (await session.execute(stmt)).scalar_one_or_none()
    if sppt_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPPT tidak ditemukan")

    detail = schemas.SpptDetail(
        year=int(sppt_row.thn_pajak_sppt),
        nop=compose_nop(fields),
        luas_bumi=float(sppt_row.luas_bumi_sppt or 0),
        luas_bangunan=float(sppt_row.luas_bng_sppt or 0),
        pbb_terhutang=float(sppt_row.pbb_terhutang_sppt or 0),
        pbb_harus_bayar=float(getattr(sppt_row, "pbb_yg_harus_dibayar_sppt", 0) or 0),
    )

    data = schemas.EspptData(
        spop=_spop_to_response(fields, spop),
        subjek_pajak=_subjek_to_response(subjek) if subjek else None,
        sppt=detail,
    )

    return schemas.EspptResponse(message="Data e-SPPT", data=data)


@router.post("/years", response_model=schemas.YearsResponse)
async def get_sppt_years(
    payload: schemas.YearsRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schemas.YearsResponse:
    fields = parse_nop(payload.nop)

    stmt = (
        select(func.distinct(Sppt.thn_pajak_sppt))
        .where(
            and_(
                Sppt.kd_propinsi == fields["kd_propinsi"],
                Sppt.kd_dati2 == fields["kd_dati2"],
                Sppt.kd_kecamatan == fields["kd_kecamatan"],
                Sppt.kd_kelurahan == fields["kd_kelurahan"],
                Sppt.kd_blok == fields["kd_blok"],
                Sppt.no_urut == fields["no_urut"],
                Sppt.kd_jns_op == fields["kd_jns_op"],
            )
        )
        .order_by(Sppt.thn_pajak_sppt.desc())
    )

    result = await session.execute(stmt)
    years = [int(year) for (year,) in result if year and str(year).isdigit()]

    if not years:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data SPPT tidak ditemukan")

    return schemas.YearsResponse(message="Daftar tahun SPPT berhasil diambil", data=years)


@router.get("/{year}/{nop}", response_model=schemas.SpptDetailResponse)
async def get_sppt_detail(
    year: int,
    nop: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schemas.SpptDetailResponse:
    fields = parse_nop(nop)

    stmt = select(Sppt).where(
        and_(
            Sppt.kd_propinsi == fields["kd_propinsi"],
            Sppt.kd_dati2 == fields["kd_dati2"],
            Sppt.kd_kecamatan == fields["kd_kecamatan"],
            Sppt.kd_kelurahan == fields["kd_kelurahan"],
            Sppt.kd_blok == fields["kd_blok"],
            Sppt.no_urut == fields["no_urut"],
            Sppt.kd_jns_op == fields["kd_jns_op"],
            Sppt.thn_pajak_sppt == str(year),
        )
    )

    result = await session.execute(stmt)
    sppt = result.scalar_one_or_none()
    if sppt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPPT tidak ditemukan")

    detail = schemas.SpptDetail(
        year=int(sppt.thn_pajak_sppt),
        nop=compose_nop(fields),
        luas_bumi=float(sppt.luas_bumi_sppt or 0),
        luas_bangunan=float(sppt.luas_bng_sppt or 0),
        pbb_terhutang=float(sppt.pbb_terhutang_sppt or 0),
        pbb_harus_bayar=float(sppt.pbb_yg_harus_dibayar_sppt or 0),
    )

    return schemas.SpptDetailResponse(message="Data SPPT berhasil diambil", data=detail)


@router.get("/batch/{nop}", response_model=schemas.SpptBatchResponse)
async def get_sppt_batch(
    nop: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schemas.SpptBatchResponse:
    fields = parse_nop(nop)

    stmt = (
        select(Sppt)
        .where(
            and_(
                Sppt.kd_propinsi == fields["kd_propinsi"],
                Sppt.kd_dati2 == fields["kd_dati2"],
                Sppt.kd_kecamatan == fields["kd_kecamatan"],
                Sppt.kd_kelurahan == fields["kd_kelurahan"],
                Sppt.kd_blok == fields["kd_blok"],
                Sppt.no_urut == fields["no_urut"],
                Sppt.kd_jns_op == fields["kd_jns_op"],
            )
        )
        .order_by(Sppt.thn_pajak_sppt.desc())
    )

    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SPPT tidak ditemukan")

    data = [
        schemas.SpptDetail(
            year=int(row.thn_pajak_sppt),
            nop=compose_nop(fields),
            luas_bumi=float(row.luas_bumi_sppt or 0),
            luas_bangunan=float(row.luas_bng_sppt or 0),
            pbb_terhutang=float(row.pbb_terhutang_sppt or 0),
            pbb_harus_bayar=float(row.pbb_yg_harus_dibayar_sppt or 0),
        )
        for row in rows
    ]

    return schemas.SpptBatchResponse(message="Data SPPT berhasil diambil", data=data)




