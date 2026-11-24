from datetime import date
from typing import Any, Dict, List, Optional

from config.settings import HARI_KERJA_PER_BULAN_BAKU, BULAN_PER_TAHUN_BAKU


def buat_peramalan_regresi_linear(
    data_tahunan: List[Dict[str, Any]],
    jumlah_periode: int = 3,
    tanggal_acuan: Optional[date] = None,
) -> Dict[str, Any]:
    """Meramalkan permintaan tahunan dengan metode tren Least Squares."""
    if jumlah_periode <= 0:
        raise ValueError("Jumlah periode peramalan harus lebih besar dari 0")
    if not data_tahunan:
        raise ValueError("Riwayat permintaan tahunan belum tersedia")

    tanggal_acuan = tanggal_acuan or date.today()
    permintaan_berdasarkan_tahun = {
        int(baris["tahun"]): float(baris["total_kuantitas"])
        for baris in data_tahunan
    }
    if any(nilai < 0 for nilai in permintaan_berdasarkan_tahun.values()):
        raise ValueError("Permintaan tahunan tidak boleh negatif")

    tahun_awal = min(permintaan_berdasarkan_tahun)
    tahun_terakhir = max(max(permintaan_berdasarkan_tahun), tanggal_acuan.year)
    permintaan_historis = []
    hari_kerja_per_tahun = HARI_KERJA_PER_BULAN_BAKU * BULAN_PER_TAHUN_BAKU

    for tahun in range(tahun_awal, tahun_terakhir + 1):
        permintaan = permintaan_berdasarkan_tahun.get(tahun, 0.0)
        if tahun == tanggal_acuan.year:
            hari_kerja_berjalan = (
                (tanggal_acuan.month - 1) * HARI_KERJA_PER_BULAN_BAKU
                + min(tanggal_acuan.day, HARI_KERJA_PER_BULAN_BAKU)
            )
            if hari_kerja_berjalan:
                permintaan *= hari_kerja_per_tahun / hari_kerja_berjalan

        permintaan_historis.append(
            {"tahun": tahun, "permintaan_tahunan": permintaan}
        )

    nilai_y = [baris["permintaan_tahunan"] for baris in permintaan_historis]
    nilai_x = list(range(1, len(nilai_y) + 1))
    rata_rata_x = sum(nilai_x) / len(nilai_x)
    rata_rata_y = sum(nilai_y) / len(nilai_y)
    penyebut = sum((x - rata_rata_x) ** 2 for x in nilai_x)
    kemiringan = (
        sum(
            (x - rata_rata_x) * (y - rata_rata_y)
            for x, y in zip(nilai_x, nilai_y)
        )
        / penyebut
        if penyebut
        else 0.0
    )
    intersep = rata_rata_y - kemiringan * rata_rata_x

    ramalan = []
    for urutan in range(1, jumlah_periode + 1):
        x = len(nilai_y) + urutan
        ramalan.append(
            {
                "tahun": tahun_terakhir + urutan,
                "periode_x": x,
                "permintaan_tahunan": round(intersep + kemiringan * x, 1),
            }
        )

    return {
        "historis": [
            {
                **baris,
                "permintaan_tahunan": round(baris["permintaan_tahunan"], 1),
            }
            for baris in permintaan_historis
        ],
        "intersep": intersep,
        "kemiringan": kemiringan,
        "persamaan": f"y = {intersep:.1f} + {kemiringan:.1f}x",
        "ramalan": ramalan,
    }
