import math
from typing import Dict

def hitung_kuantitas_pemesanan_ekonomis(
    permintaan_tahunan: float,
    biaya_pemesanan: float,
    biaya_penyimpanan_per_unit_tahun: float,
) -> float:
    """
    Menghitung Economic Order Quantity (EOQ).
    Rumus: sqrt((2 * D * S) / H)
    - D: Annual Demand (Permintaan tahunan)
    - S: Ordering Cost (Biaya pemesanan per pesanan)
    - H: Holding Cost (Biaya penyimpanan per satuan per tahun)
    """
    if permintaan_tahunan <= 0:
        raise ValueError("Permintaan tahunan (tahunan demand) harus > 0")
    if biaya_pemesanan < 0:
        raise ValueError("Biaya pemesanan (ordering biaya) tidak boleh negatif")
    if biaya_penyimpanan_per_unit_tahun <= 0:
        raise ValueError("Biaya penyimpanan per satuan (holding biaya) harus > 0")

    nilai_kuantitas_pemesanan = math.sqrt((2 * float(permintaan_tahunan) * float(biaya_pemesanan)) / float(biaya_penyimpanan_per_unit_tahun))
    return round(nilai_kuantitas_pemesanan, 2)


def hitung_stok_pengaman(
    simpangan_baku_permintaan_harian: float,
    waktu_tunggu_hari: float,
    skor_z: float = 1.65,
) -> float:
    """
    Menghitung Safety Stock (Persediaan Pengaman).
    Rumus: Z * stddev_d * sqrt(L)
    - Z: Service level factor (misal 1.65 untuk tingkat pelayanan ~95%)
    - stddev_d: Standar deviasi permintaan harian
    - L: Waktu tunggu (lead time dalam hari)
    """
    if simpangan_baku_permintaan_harian < 0:
        raise ValueError("Standar deviasi permintaan tidak boleh negatif")
    if waktu_tunggu_hari < 0:
        raise ValueError("Lead time tidak boleh negatif")
    if skor_z < 0:
        raise ValueError("Nilai Z-score tidak boleh negatif")

    nilai_stok_pengaman = float(skor_z) * float(simpangan_baku_permintaan_harian) * math.sqrt(float(waktu_tunggu_hari))
    return round(nilai_stok_pengaman, 2)


def hitung_titik_pemesanan_ulang(
    rata_rata_permintaan_harian: float,
    waktu_tunggu_hari: float,
    stok_pengaman: float,
) -> float:
    """
    Menghitung Reorder Point (Titik Pemesanan Kembali).
    Rumus: (d * L) + SS
    - d: Rata-rata permintaan harian
    - L: Lead time dalam hari
    - SS: Safety Stock
    """
    if rata_rata_permintaan_harian < 0:
        raise ValueError("Rata-rata permintaan harian tidak boleh negatif")
    if waktu_tunggu_hari < 0:
        raise ValueError("Lead time tidak boleh negatif")
    if stok_pengaman < 0:
        raise ValueError("Safety stok tidak boleh negatif")

    nilai_titik_pemesanan_ulang = (float(rata_rata_permintaan_harian) * float(waktu_tunggu_hari)) + float(stok_pengaman)
    return round(nilai_titik_pemesanan_ulang, 2)


def hitung_biaya_persediaan(
    permintaan_tahunan: float,
    kuantitas_pemesanan: float,
    biaya_pemesanan: float,
    biaya_penyimpanan_per_unit_tahun: float,
) -> Dict[str, float]:
    """
    Menghitung total biaya persediaan berdasarkan kuantitas pesanan.
    - Annual Ordering Cost = (D / Q) * S
    - Annual Holding Cost = (Q / 2) * H
    - Total Variable Cost = Ordering Cost + Holding Cost
    """
    permintaan = float(permintaan_tahunan)
    kuantitas = float(kuantitas_pemesanan)
    elemen = float(biaya_pemesanan)
    biaya_simpan = float(biaya_penyimpanan_per_unit_tahun)

    if kuantitas <= 0:
        raise ValueError("Kuantitas pemesanan (Q) harus > 0")

    biaya_pemesanan_tahunan = (permintaan / kuantitas) * elemen
    biaya_penyimpanan_tahunan = (kuantitas / 2) * biaya_simpan
    total_biaya = biaya_pemesanan_tahunan + biaya_penyimpanan_tahunan
    jumlah_pemesanan = permintaan / kuantitas
    hari_siklus_pemesanan = (kuantitas / permintaan) * 365 if permintaan > 0 else 0

    return {
        "kuantitas_pemesanan": round(kuantitas, 2),
        "biaya_pemesanan_tahunan": round(biaya_pemesanan_tahunan, 2),
        "biaya_penyimpanan_tahunan": round(biaya_penyimpanan_tahunan, 2),
        "total_biaya": round(total_biaya, 2),
        "jumlah_pemesanan_per_tahun": round(jumlah_pemesanan, 2),
        "hari_siklus_pemesanan": round(hari_siklus_pemesanan, 1),
    }


def analisis_item_persediaan(
    permintaan_tahunan: float,
    biaya_pemesanan: float,
    biaya_penyimpanan_per_unit_tahun: float,
    rata_rata_permintaan_harian: float,
    simpangan_baku_permintaan_harian: float,
    waktu_tunggu_hari: float,
    skor_z: float = 1.65,
) -> Dict[str, float]:
    """
    Melakukan perhitungan menyeluruh untuk satu elemen inventaris.
    """
    kuantitas_pemesanan_ekonomis = hitung_kuantitas_pemesanan_ekonomis(permintaan_tahunan, biaya_pemesanan, biaya_penyimpanan_per_unit_tahun)
    stok_pengaman = hitung_stok_pengaman(simpangan_baku_permintaan_harian, waktu_tunggu_hari, skor_z)
    titik_pemesanan_ulang = hitung_titik_pemesanan_ulang(rata_rata_permintaan_harian, waktu_tunggu_hari, stok_pengaman)
    biaya = hitung_biaya_persediaan(permintaan_tahunan, kuantitas_pemesanan_ekonomis, biaya_pemesanan, biaya_penyimpanan_per_unit_tahun)

    return {
        "kuantitas_pemesanan_ekonomis": kuantitas_pemesanan_ekonomis,
        "stok_pengaman": stok_pengaman,
        "titik_pemesanan_ulang": titik_pemesanan_ulang,
        **biaya,
    }
