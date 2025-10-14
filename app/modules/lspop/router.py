from __future__ import annotations

from secrets import randbelow
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import and_, select

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.dashboards.models import DatOpBangunan
from app.modules.lspop.schemas import LspopCreatePayload, LspopCreateResponse, LspopDetail

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


def _extract_keys(payload: LspopCreatePayload) -> Dict[str, str]:
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


def _record_to_detail(record: DatOpBangunan) -> LspopDetail:
    return LspopDetail(
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


@router.post("", response_model=LspopCreateResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", response_model=LspopCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_lspop(
    payload: LspopCreatePayload,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> LspopCreateResponse:
    keys = _extract_keys(payload)

    stmt = select(DatOpBangunan).where(
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
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data LSPOP untuk bangunan tersebut sudah terdaftar",
        )

    form_number = payload.no_formulir_lspop or await _generate_form_number(session)

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
    return LspopCreateResponse(message="LSPOP berhasil ditambahkan", data=detail)
