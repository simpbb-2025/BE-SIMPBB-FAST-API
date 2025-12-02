from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import SessionDep
from app.modules.dropdown import schemas
from app.modules.spop.models import (
    RefJenisTanah,
    RefKabupaten,
    RefKecamatanBaru,
    RefKelurahanBaru,
    RefPekerjaanSubjek,
    RefProvinsi,
    RefStatusSubjek,
)
from app.modules.lspop.models import (
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
from app.modules.spop.models import RefKelasBumiNjop, RefKelasBangunanNjop


router = APIRouter(prefix="/dropdown", tags=["dropdown"])


async def _load_region_dropdown(session: SessionDep):
    prov_rows = await session.execute(select(RefProvinsi.id_provinsi, RefProvinsi.kode_provinsi, RefProvinsi.nama_provinsi))
    kab_rows = await session.execute(select(RefKabupaten.id_kabupaten, RefKabupaten.kode_kabupaten, RefKabupaten.nama_kabupaten))
    kec_rows = await session.execute(
        select(RefKecamatanBaru.id_kecamatan, RefKecamatanBaru.kode_kecamatan, RefKecamatanBaru.nama_kecamatan)
    )
    kel_rows = await session.execute(
        select(RefKelurahanBaru.id_kelurahan, RefKelurahanBaru.kode_kelurahan, RefKelurahanBaru.nama_kelurahan)
    )

    prov = [schemas.DropdownRegion(id=row.id_provinsi, kode=f"{row.kode_provinsi:02d}", nama=row.nama_provinsi) for row in prov_rows]
    kab = [schemas.DropdownRegion(id=row.id_kabupaten, kode=f"{row.kode_kabupaten:02d}", nama=row.nama_kabupaten) for row in kab_rows]
    kec = [schemas.DropdownRegion(id=row.id_kecamatan, kode=f"{row.kode_kecamatan:03d}", nama=row.nama_kecamatan) for row in kec_rows]
    kel = [schemas.DropdownRegion(id=row.id_kelurahan, kode=f"{row.kode_kelurahan:03d}", nama=row.nama_kelurahan) for row in kel_rows]

    return prov, kab, kec, kel


@router.get("/spop", response_model=schemas.DropdownResponse)
async def dropdown_spop(session: SessionDep) -> schemas.DropdownResponse:
    prov, kab, kec, kel = await _load_region_dropdown(session)
    status_rows = await session.execute(select(RefStatusSubjek.id, RefStatusSubjek.nama))
    kerja_rows = await session.execute(select(RefPekerjaanSubjek.id, RefPekerjaanSubjek.nama))
    tanah_rows = await session.execute(select(RefJenisTanah.id, RefJenisTanah.nama))

    status = [schemas.DropdownSimple(id=row.id, nama=row.nama) for row in status_rows]
    kerja = [schemas.DropdownSimple(id=row.id, nama=row.nama) for row in kerja_rows]
    tanah = [schemas.DropdownSimple(id=row.id, nama=row.nama) for row in tanah_rows]

    return schemas.DropdownResponse(
        message="Data dropdown berhasil diambil",
        provinsi=prov,
        kabupaten_kota=kab,
        kecamatan=kec,
        kelurahan_desa=kel,
        status_subjek=status,
        pekerjaan_subjek=kerja,
        jenis_tanah=tanah,
    )


@router.get("/alamat-subjek", response_model=schemas.DropdownBasicResponse)
async def dropdown_spop_basic(session: SessionDep) -> schemas.DropdownBasicResponse:
    prov, kab, kec, kel = await _load_region_dropdown(session)
    return schemas.DropdownBasicResponse(
        message="Data dropdown wilayah berhasil diambil",
        provinsi_subjek=prov,
        kabupaten_kota_subjek=kab,
        kecamatan_subjek=kec,
        kelurahan_desa_subjek=kel,
    )


@router.get("/lspop", response_model=schemas.LspopDropdownResponse)
async def dropdown_lspop(session: SessionDep) -> schemas.LspopDropdownResponse:
    def fetch(model):
        rows = session.execute(select(model.id, model.nama))
        return rows

    jenis_penggunaan = await session.execute(select(RefJenisPenggunaanBangunan.id, RefJenisPenggunaanBangunan.nama))
    kondisi = await session.execute(select(RefKondisiBangunan.id, RefKondisiBangunan.nama))
    konstruksi = await session.execute(select(RefJenisKonstruksi.id, RefJenisKonstruksi.nama))
    atap = await session.execute(select(RefJenisAtap.id, RefJenisAtap.nama))
    lantai = await session.execute(select(RefJenisLantai.id, RefJenisLantai.nama))
    langit = await session.execute(select(RefJenisLangitLangit.id, RefJenisLangitLangit.nama))
    kelas_perkantoran = await session.execute(select(RefKelasBangunanPerkantoran.id, RefKelasBangunanPerkantoran.nama))
    kelas_ruko = await session.execute(select(RefKelasBangunanRuko.id, RefKelasBangunanRuko.nama))
    kelas_rs = await session.execute(select(RefKelasBangunanRumahSakit.id, RefKelasBangunanRumahSakit.nama))
    kelas_olahraga = await session.execute(select(RefKelasBangunanOlahraga.id, RefKelasBangunanOlahraga.nama))
    jenis_hot = await session.execute(select(RefJenisHotel.id, RefJenisHotel.nama))
    bintang_hot = await session.execute(select(RefBintangHotel.id, RefBintangHotel.nama))
    kelas_parkir = await session.execute(select(RefKelasBangunanParkir.id, RefKelasBangunanParkir.nama))
    kelas_apart = await session.execute(select(RefKelasBangunanApartemen.id, RefKelasBangunanApartemen.nama))
    kelas_sekolah = await session.execute(select(RefKelasBangunanSekolah.id, RefKelasBangunanSekolah.nama))
    letak_tangki = await session.execute(select(RefLetakTangkiMinyak.id, RefLetakTangkiMinyak.nama))

    def to_simple(rows):
        return [schemas.DropdownSimple(id=row.id, nama=row.nama) for row in rows]

    return schemas.LspopDropdownResponse(
        message="Data dropdown LSPOP berhasil diambil",
        jenis_penggunaan_bangunan=to_simple(jenis_penggunaan),
        kondisi_bangunan=to_simple(kondisi),
        jenis_konstruksi=to_simple(konstruksi),
        jenis_atap=to_simple(atap),
        jenis_lantai=to_simple(lantai),
        jenis_langit_langit=to_simple(langit),
        kelas_bangunan_perkantoran=to_simple(kelas_perkantoran),
        kelas_bangunan_ruko=to_simple(kelas_ruko),
        kelas_bangunan_rumah_sakit=to_simple(kelas_rs),
        kelas_bangunan_olahraga=to_simple(kelas_olahraga),
        jenis_hotel=to_simple(jenis_hot),
        bintang_hotel=to_simple(bintang_hot),
        kelas_bangunan_parkir=to_simple(kelas_parkir),
        kelas_bangunan_apartemen=to_simple(kelas_apart),
        kelas_bangunan_sekolah=to_simple(kelas_sekolah),
        letak_tangki_minyak=to_simple(letak_tangki),
    )


@router.get("/kelas-njop", response_model=schemas.KelasNjopDropdownResponse)
async def dropdown_kelas_njop(session: SessionDep) -> schemas.KelasNjopDropdownResponse:
    bumi_rows = await session.execute(
        select(RefKelasBumiNjop.id, RefKelasBumiNjop.kelas, RefKelasBumiNjop.njop)
    )
    bangunan_rows = await session.execute(
        select(RefKelasBangunanNjop.id, RefKelasBangunanNjop.kelas, RefKelasBangunanNjop.njop)
    )

    def to_kelas(rows):
        return [
            schemas.DropdownKelasNjop(id=row.id, kelas=str(row.kelas), njop=int(row.njop))
            for row in rows
        ]

    return schemas.KelasNjopDropdownResponse(
        message="Data dropdown kelas NJOP berhasil diambil",
        kelas_bumi_njop=to_kelas(bumi_rows),
        kelas_bangunan_njop=to_kelas(bangunan_rows),
    )
