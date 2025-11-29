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


router = APIRouter(prefix="/dropdown", tags=["dropdown"])


@router.get("/spop", response_model=schemas.DropdownResponse)
async def dropdown_spop(session: SessionDep) -> schemas.DropdownResponse:
    prov_rows = await session.execute(select(RefProvinsi.id_provinsi, RefProvinsi.kode_provinsi, RefProvinsi.nama_provinsi))
    kab_rows = await session.execute(select(RefKabupaten.id_kabupaten, RefKabupaten.kode_kabupaten, RefKabupaten.nama_kabupaten))
    kec_rows = await session.execute(
        select(RefKecamatanBaru.id_kecamatan, RefKecamatanBaru.kode_kecamatan, RefKecamatanBaru.nama_kecamatan)
    )
    kel_rows = await session.execute(
        select(RefKelurahanBaru.id_kelurahan, RefKelurahanBaru.kode_kelurahan, RefKelurahanBaru.nama_kelurahan)
    )
    status_rows = await session.execute(select(RefStatusSubjek.id, RefStatusSubjek.nama))
    kerja_rows = await session.execute(select(RefPekerjaanSubjek.id, RefPekerjaanSubjek.nama))
    tanah_rows = await session.execute(select(RefJenisTanah.id, RefJenisTanah.nama))

    prov = [schemas.DropdownRegion(id=row.id_provinsi, kode=f"{row.kode_provinsi:02d}", nama=row.nama_provinsi) for row in prov_rows]
    kab = [schemas.DropdownRegion(id=row.id_kabupaten, kode=f"{row.kode_kabupaten:02d}", nama=row.nama_kabupaten) for row in kab_rows]
    kec = [schemas.DropdownRegion(id=row.id_kecamatan, kode=f"{row.kode_kecamatan:03d}", nama=row.nama_kecamatan) for row in kec_rows]
    kel = [schemas.DropdownRegion(id=row.id_kelurahan, kode=f"{row.kode_kelurahan:03d}", nama=row.nama_kelurahan) for row in kel_rows]
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
