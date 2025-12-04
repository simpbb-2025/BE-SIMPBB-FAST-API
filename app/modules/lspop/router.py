from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import MissingGreenlet, OperationalError

from app.core.config import settings
from app.core.deps import CurrentUserDep, SessionDep
from app.modules.lspop import schemas
from app.modules.lspop.models import (
    LampiranSpop,
    RefJenisPenggunaanBangunan,
    RefKondisiBangunan,
    RefJenisKonstruksi,
    RefJenisAtap,
    RefJenisLantai,
    RefJenisLangitLangit,
    RefKelasBangunanPerkantoran,
    RefKelasBangunanRuko,
    RefKelasBangunanRumahSakit,
    RefKelasBangunanOlahraga,
    RefJenisHotel,
    RefBintangHotel,
    RefKelasBangunanParkir,
    RefKelasBangunanApartemen,
    RefKelasBangunanSekolah,
    RefLetakTangkiMinyak,
)
from app.modules.spop.models import RefKelasBangunanNjop, RefKelasBumiNjop, SpopRegistration

router = APIRouter(prefix="/lspop", tags=["lspop"])


def _to_record(
    row: LampiranSpop,
    lookups: Optional[dict] = None,
    spop_map: Optional[Dict[str, schemas.SpopInfo]] = None,
    kelas_map: Optional[Dict[int, schemas.NjopClass]] = None,
) -> schemas.LampiranRecord:
    lookups = lookups or {}
    spop_data = (spop_map or {}).get(row.spop_id)
    kelas_obj = None
    if row.kelas_bangunan_njop is not None:
        kelas_obj = (kelas_map or {}).get(row.kelas_bangunan_njop)

    def info(field: str, value: Optional[int]) -> Optional[schemas.StatusInfo]:
        if value is None:
            return None
        return schemas.StatusInfo(id=value, nama=lookups.get(field, {}).get(value, ""))

    return schemas.LampiranRecord(
        id=row.id,
        submitted_at=row.submitted_at,
        data_spop=spop_data,
        no_formulir=row.no_formulir,
        nama_petugas=row.nama_petugas,
        nip=row.nip,
        kelas_bangunan_njop=kelas_obj,
        tanggal_pelaksanaan=row.tanggal_pelaksanaan,
        status=row.status,
        nop=row.nop,
        jumlah_bangunan=row.jumlah_bangunan,
        bangunan_ke=row.bangunan_ke,
        jenis_penggunaan_bangunan=info("jenis_penggunaan_bangunan", row.jenis_penggunaan_bangunan),
        kondisi_bangunan=info("kondisi_bangunan", row.kondisi_bangunan),
        tahun_dibangun=row.tahun_dibangun,
        tahun_direnovasi=row.tahun_direnovasi,
        luas_bangunan_m2=row.luas_bangunan_m2,
        jumlah_lantai=row.jumlah_lantai,
        daya_listrik_watt=row.daya_listrik_watt,
        jenis_konstruksi=info("jenis_konstruksi", row.jenis_konstruksi),
        jenis_atap=info("jenis_atap", row.jenis_atap),
        jenis_lantai=info("jenis_lantai", row.jenis_lantai),
        jenis_langit_langit=info("jenis_langit_langit", row.jenis_langit_langit),
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
        kelas_bangunan_perkantoran=info("kelas_bangunan_perkantoran", row.kelas_bangunan_perkantoran),
        kelas_bangunan_ruko=info("kelas_bangunan_ruko", row.kelas_bangunan_ruko),
        kelas_bangunan_rumah_sakit=info("kelas_bangunan_rumah_sakit", row.kelas_bangunan_rumah_sakit),
        luas_ruang_kamar_ac_sentral_m2=row.luas_ruang_kamar_ac_sentral_m2,
        luas_ruang_lain_ac_sentral_m2=row.luas_ruang_lain_ac_sentral_m2,
        kelas_bangunan_olahraga=info("kelas_bangunan_olahraga", row.kelas_bangunan_olahraga),
        jenis_hotel=info("jenis_hotel", row.jenis_hotel),
        bintang_hotel=info("bintang_hotel", row.bintang_hotel),
        jumlah_kamar_hotel=row.jumlah_kamar_hotel,
        luas_ruang_kamar_hotel_ac_sentral_m2=row.luas_ruang_kamar_hotel_ac_sentral_m2,
        luas_ruang_lain_hotel_ac_sentral_m2=row.luas_ruang_lain_hotel_ac_sentral_m2,
        kelas_bangunan_parkir=info("kelas_bangunan_parkir", row.kelas_bangunan_parkir),
        kelas_bangunan_apartemen=info("kelas_bangunan_apartemen", row.kelas_bangunan_apartemen),
        jumlah_kamar_apartemen=row.jumlah_kamar_apartemen,
        letak_tangki_minyak=info("letak_tangki_minyak", row.letak_tangki_minyak),
        kapasitas_tangki_minyak_liter=row.kapasitas_tangki_minyak_liter,
        kelas_bangunan_sekolah=info("kelas_bangunan_sekolah", row.kelas_bangunan_sekolah),
        foto_objek_pajak=row.foto_objek_pajak,
    )


async def _build_lookups(session: SessionDep, rows: List[LampiranSpop]) -> dict:
    fields_models = {
        "jenis_penggunaan_bangunan": RefJenisPenggunaanBangunan,
        "kondisi_bangunan": RefKondisiBangunan,
        "jenis_konstruksi": RefJenisKonstruksi,
        "jenis_atap": RefJenisAtap,
        "jenis_lantai": RefJenisLantai,
        "jenis_langit_langit": RefJenisLangitLangit,
        "kelas_bangunan_perkantoran": RefKelasBangunanPerkantoran,
        "kelas_bangunan_ruko": RefKelasBangunanRuko,
        "kelas_bangunan_rumah_sakit": RefKelasBangunanRumahSakit,
        "kelas_bangunan_olahraga": RefKelasBangunanOlahraga,
        "jenis_hotel": RefJenisHotel,
        "bintang_hotel": RefBintangHotel,
        "kelas_bangunan_parkir": RefKelasBangunanParkir,
        "kelas_bangunan_apartemen": RefKelasBangunanApartemen,
        "kelas_bangunan_sekolah": RefKelasBangunanSekolah,
        "letak_tangki_minyak": RefLetakTangkiMinyak,
    }

    id_sets: dict = {field: set() for field in fields_models}
    for row in rows:
        for field in fields_models:
            val = getattr(row, field, None)
            if val is not None:
                id_sets[field].add(val)

    lookups: dict = {}
    for field, model in fields_models.items():
        ids = id_sets[field]
        if not ids:
            lookups[field] = {}
            continue
        rows_db = await session.execute(select(model.id, model.nama).where(model.id.in_(ids)))
        lookups[field] = {r.id: r.nama for r in rows_db}
    return lookups


async def _build_kelas_bangunan_map(session: SessionDep, rows: List[LampiranSpop]) -> Dict[int, schemas.NjopClass]:
    ids = {row.kelas_bangunan_njop for row in rows if row.kelas_bangunan_njop is not None}
    if not ids:
        return {}
    result = await session.execute(select(RefKelasBangunanNjop).where(RefKelasBangunanNjop.id.in_(ids)))
    kelas_map: Dict[int, schemas.NjopClass] = {}
    for row in result.scalars():
        kelas_value = getattr(row, "kelas", None)
        kelas_str = str(kelas_value) if kelas_value is not None else None
        kelas_map[row.id] = schemas.NjopClass(id=row.id, kelas=kelas_str, njop=getattr(row, "njop", None))
    return kelas_map


async def _build_spop_map(session: SessionDep, rows: List[LampiranSpop]) -> Dict[str, schemas.SpopInfo]:
    spop_ids = {row.spop_id for row in rows if row.spop_id}
    if not spop_ids:
        return {}
    result = await session.execute(
        select(
            SpopRegistration.id,
            SpopRegistration.nama_lengkap,
            SpopRegistration.nama_awal,
            SpopRegistration.status,
        ).where(SpopRegistration.id.in_(spop_ids))
    )
    spop_map: Dict[str, schemas.SpopInfo] = {}
    for row in result:
        nama = row.nama_lengkap or row.nama_awal
        spop_map[row.id] = schemas.SpopInfo(nama=nama, status_akhir=row.status)
    return spop_map


async def _get_spop_by_nop(session: SessionDep, nop: str) -> SpopRegistration:
    if not nop:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP wajib diisi")
    row = (
        await session.execute(select(SpopRegistration).where(SpopRegistration.nop == nop).limit(1))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP tidak ditemukan di SPOP")
    status_value = (row.status or "").strip().lower()
    if status_value != "disetujui":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NOP hanya bisa dipakai jika SPOP telah berstatus disetujui",
        )
    return row


async def _load_payload(request: Request, model_cls):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    for key in ("_method", "_put", "_patch"):
        data.pop(key, None)
    if model_cls is schemas.LampiranStaffPayload:
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "":
                cleaned[key] = None
            else:
                cleaned[key] = value
        data = cleaned
    return model_cls(**data)


def _safe_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _normalize_nop_digits(raw_nop: Optional[str]) -> str:
    digits = "".join(ch for ch in (raw_nop or "") if ch.isdigit())
    if len(digits) != 18:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP harus 18 digit")
    return digits


def _normalize_label(text: str) -> str:
    # Buang digit dan whitespace, lowercase, untuk mencocokkan "1 Kabupaten Badung" == "Kabupaten Badung"
    clean = "".join(ch for ch in (text or "") if not ch.isdigit())
    return clean.strip().lower()


async def _njop_value(session: SessionDep, model, class_id: Optional[int]) -> int:
    if class_id is None:
        return 0
    row = await session.get(model, class_id)
    if row is None:
        return 0
    return _safe_int(getattr(row, "njop", 0))


async def _pick_pbb_tarif(session: SessionDep, spop_row: SpopRegistration) -> tuple[int, Decimal]:
    """
    Pilih tarif PBB dari tabel pbb_p2:
    1) Jika PBB_TARIF_ID di env, wajib ada baris itu.
    2) Jika tidak, pakai nama kabupaten (kabupaten_kota.nama_kabupaten) yang dicocokkan dengan pbb_p2.daerah (tanpa angka, case-insensitive).
    Kolom yang dipakai: pbb_persen (angka desimal, misal 0.2).
    """
    # 1. Env override
    if settings.pbb_tarif_id is not None:
        result = await session.execute(
            text("SELECT id, pbb_persen FROM pbb_p2 WHERE id = :id LIMIT 1"),
            {"id": settings.pbb_tarif_id},
        )
        row = result.first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tarif PBB_TARIF_ID tidak ditemukan di pbb_p2",
            )
        return _safe_int(row[0]), Decimal(row[1] or 0)

    # 2. Berdasarkan nama kabupaten
    kab_id = _safe_int(spop_row.kabupaten_op)
    if kab_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="kabupaten_op tidak valid untuk menentukan tarif PBB",
        )

    # Ambil nama kabupaten lalu cocokan dengan pbb_p2.daerah (normalisasi nama buang angka)
    try:
        kab_row = await session.execute(
            text("SELECT nama_kabupaten FROM kabupaten_kota WHERE id_kabupaten = :id LIMIT 1"),
            {"id": kab_id},
        )
        kab_name_row = kab_row.first()
        kab_name = _normalize_label(kab_name_row[0]) if kab_name_row and kab_name_row[0] else ""
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kolom/struktur kabupaten_kota tidak sesuai: {exc}",
        ) from exc

    if not kab_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama kabupaten tidak ditemukan untuk menentukan tarif PBB",
        )

    try:
        pbb_rows = await session.execute(text("SELECT id, daerah, pbb_persen FROM pbb_p2"))
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kolom/struktur pbb_p2 tidak sesuai: {exc}",
        ) from exc

    match_id: Optional[int] = None
    match_rate = Decimal(0)
    for r in pbb_rows:
        daerah_norm = _normalize_label(r.daerah)
        if daerah_norm == kab_name:
            match_id = _safe_int(r.id)
            match_rate = Decimal(r.pbb_persen or 0)
            break

    if match_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tarif PBB untuk kabupaten_op tidak ditemukan di pbb_p2 (cocokkan nama daerah)",
        )

    return match_id, match_rate


# Create SPPT automatically only when related SPOP is approved.
async def _create_sppt_for_lspop(
    session: SessionDep,
    lspop: LampiranSpop,
    spop_row: Optional[SpopRegistration] = None,
) -> Optional[schemas.SpptAutoRecord]:
    if spop_row is None:
        spop_row = (
            await session.execute(select(SpopRegistration).where(SpopRegistration.nop == lspop.nop).limit(1))
        ).scalar_one_or_none()
        if spop_row is None:
            return None

    status_value = (spop_row.status or "").strip().lower()
    if status_value != "disetujui":
        return None

    nop_digits = _normalize_nop_digits(lspop.nop)
    spop_nop_digits = _normalize_nop_digits(spop_row.nop)
    if nop_digits != spop_nop_digits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NOP LSPOP tidak sama dengan SPOP")

    bumi_rate = await _njop_value(session, RefKelasBumiNjop, spop_row.kelas_bumi_njop)
    bangunan_rate = await _njop_value(session, RefKelasBangunanNjop, spop_row.kelas_bangunan_njop)

    bumi_njop = _safe_int(spop_row.luas_tanah) * bumi_rate
    bangunan_njop = _safe_int(lspop.luas_bangunan_m2) * bangunan_rate
    total_njop = bumi_njop + bangunan_njop

    njoptkp = _safe_int(settings.pbb_njoptkp)
    tarif_id, tarif_decimal = await _pick_pbb_tarif(session, spop_row)

    dasar_pengenaan = Decimal(total_njop) - Decimal(njoptkp)
    if dasar_pengenaan < 0:
        dasar_pengenaan = Decimal(0)
    pbb_terhutang = int((dasar_pengenaan * tarif_decimal).quantize(Decimal("1."), rounding=ROUND_HALF_UP))

    now = datetime.utcnow()

    sppt_id = uuid4().hex
    await session.execute(
        text(
            """
            INSERT INTO sppt (
                id, spop_id, lspop_id, nop, bumi_njop, bangunan_njop, njoptkp, pbb_persen, create_at
            ) VALUES (
                :id, :spop_id, :lspop_id, :nop, :bumi_njop, :bangunan_njop, :njoptkp, :pbb_persen, :create_at
            )
            """
        ),
        {
            "id": sppt_id,
            "spop_id": spop_row.id,
            "lspop_id": lspop.id,
            "nop": nop_digits,
            "bumi_njop": bumi_njop,
            "bangunan_njop": bangunan_njop,
            "njoptkp": njoptkp,
            "pbb_persen": tarif_id,
            "create_at": now,
        },
    )
    await session.commit()

    return schemas.SpptAutoRecord(
        id=sppt_id,
        spop_id=spop_row.id,
        lspop_id=lspop.id,
        nop=nop_digits,
        bumi_njop=bumi_njop,
        bangunan_njop=bangunan_njop,
        create_at=now,
    )


@router.post("", response_model=schemas.LampiranResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.LampiranResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_lspop(
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranResponse:
    payload = await _load_payload(request, schemas.LampiranCreatePayload)
    spop_row = await _get_spop_by_nop(session, payload.nop)
    entity = LampiranSpop(id=uuid4().hex)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(entity, key, value)
    entity.spop_id = spop_row.id
    entity.no_formulir = datetime.now().strftime("%Y.%m.%d.%H.%M")

    session.add(entity)
    await session.commit()
    await session.refresh(entity)

    sppt_record: Optional[schemas.SpptAutoRecord] = await _create_sppt_for_lspop(session, entity, spop_row)

    try:
        lookups = await _build_lookups(session, [entity])
    except MissingGreenlet:
        lookups = {}
    spop_map = {
        spop_row.id: schemas.SpopInfo(nama=spop_row.nama_lengkap or spop_row.nama_awal, status_akhir=spop_row.status)
    }
    kelas_map = await _build_kelas_bangunan_map(session, [entity])
    record = _to_record(entity, lookups, spop_map, kelas_map)
    return schemas.LampiranResponse(message="Lampiran SPOP berhasil dibuat", data=record, sppt=sppt_record)


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

    lookups = await _build_lookups(session, rows)
    spop_map = await _build_spop_map(session, rows)
    kelas_map = await _build_kelas_bangunan_map(session, rows)
    data: List[schemas.LampiranRecord] = [_to_record(row, lookups, spop_map, kelas_map) for row in rows]
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
    lookups = await _build_lookups(session, [entity])
    spop_map = await _build_spop_map(session, [entity])
    kelas_map = await _build_kelas_bangunan_map(session, [entity])
    record = _to_record(entity, lookups, spop_map, kelas_map)
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
    lookups = await _build_lookups(session, [entity])
    spop_map = await _build_spop_map(session, [entity])
    kelas_map = await _build_kelas_bangunan_map(session, [entity])
    record = _to_record(entity, lookups, spop_map, kelas_map)
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


@router.put("/staff/{lampiran_id}", response_model=schemas.LampiranResponse)
@router.post("/staff/{lampiran_id}", response_model=schemas.LampiranResponse, include_in_schema=False)
async def update_lspop_staff(
    lampiran_id: str,
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> schemas.LampiranResponse:
    entity = await session.get(LampiranSpop, lampiran_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lampiran tidak ditemukan")

    payload = await _load_payload(request, schemas.LampiranStaffPayload)
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    applied_changes = False
    for key, value in updates.items():
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                value = None
        if key == "kelas_bangunan_njop" and value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = None
        if value is None:
            continue
        if hasattr(entity, key):
            current_value = getattr(entity, key)
            if current_value != value:
                setattr(entity, key, value)
                applied_changes = True

    if applied_changes:
        await session.commit()
        await session.refresh(entity)
    lookups = await _build_lookups(session, [entity])
    spop_map = await _build_spop_map(session, [entity])
    kelas_map = await _build_kelas_bangunan_map(session, [entity])
    record = _to_record(entity, lookups, spop_map, kelas_map)
    return schemas.LampiranResponse(message="Data petugas LSPOP berhasil diperbarui", data=record)
