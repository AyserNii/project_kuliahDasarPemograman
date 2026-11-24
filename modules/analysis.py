import math
from typing import Any, Dict
from modules.inventory import hitung_biaya_persediaan


def tentukan_status_stok(stok_saat_ini: float, titik_pemesanan_ulang: float, stok_pengaman: float = 0) -> str:
    """
    Menentukan status kesehatan stok produk:
    - HABIS: Stok 0 atau kurang
    - KRITIS: Stok di bawah atau sama dengan Safety Stock
    - PERLU REORDER: Stok di bawah atau sama dengan Reorder Point
    - AMAN: Stok berada di atas Reorder Point
    """
    stok = float(stok_saat_ini)
    titik_pemesanan_ulang = float(titik_pemesanan_ulang)
    stok_pengaman = float(stok_pengaman)

    if stok <= 0:
        return "HABIS"
    if stok_pengaman > 0 and stok <= stok_pengaman:
        return "KRITIS"
    if stok <= titik_pemesanan_ulang:
        return "PERLU REORDER"
    return "AMAN"


def bandingkan_kebijakan_persediaan(
    permintaan_tahunan: float,
    kuantitas_pemesanan_saat_ini: float,
    kuantitas_pemesanan_ekonomis: float,
    biaya_pemesanan: float,
    biaya_penyimpanan_per_unit_tahun: float,
) -> Dict[str, Any]:
    """
    Membandingkan biaya kebijakan pemesanan konvensional (saat ini) dengan kebijakan EOQ.
    Menghitung potensi penghematan biaya operasional persediaan.
    """
    biaya_saat_ini = hitung_biaya_persediaan(
        permintaan_tahunan, kuantitas_pemesanan_saat_ini, biaya_pemesanan, biaya_penyimpanan_per_unit_tahun
    )
    biaya_pemesanan_ekonomis = hitung_biaya_persediaan(
        permintaan_tahunan, kuantitas_pemesanan_ekonomis, biaya_pemesanan, biaya_penyimpanan_per_unit_tahun
    )

    penghematan = biaya_saat_ini["total_biaya"] - biaya_pemesanan_ekonomis["total_biaya"]
    persentase_penghematan = (penghematan / biaya_saat_ini["total_biaya"] * 100) if biaya_saat_ini["total_biaya"] > 0 else 0

    return {
        "kebijakan_saat_ini": biaya_saat_ini,
        "kebijakan_pemesanan_ekonomis": biaya_pemesanan_ekonomis,
        "penghematan_tahunan": round(max(0.0, penghematan), 2),
        "persentase_penghematan": round(max(0.0, persentase_penghematan), 2),
    }


def buat_rekomendasi(
    nama_produk: str,
    stok_saat_ini: float,
    titik_pemesanan_ulang: float,
    stok_pengaman: float,
    kuantitas_pemesanan_ekonomis: float,
) -> Dict[str, Any]:
    """
    Menghasilkan rekomendasi tindakan konkret untuk manajemen persediaan barang.
    """
    status = tentukan_status_stok(stok_saat_ini, titik_pemesanan_ulang, stok_pengaman)

    if status in ("HABIS", "KRITIS", "PERLU REORDER"):
        jumlah_pemesanan = math.ceil(float(kuantitas_pemesanan_ekonomis))
        tindakan = f"Lakukan pemesanan ulang segera sebesar {jumlah_pemesanan} unit (sesuai EOQ)."
        prioritas = "TINGGI" if status in ("HABIS", "KRITIS") else "SEDANG"
    else:
        tindakan = "Stok masih mencukupi. Pertahankan tingkat persediaan saat ini."
        prioritas = "RENDAH"

    return {
        "nama_produk": nama_produk,
        "stok_saat_ini": round(float(stok_saat_ini), 2),
        "titik_pemesanan_ulang": round(float(titik_pemesanan_ulang), 2),
        "stok_pengaman": round(float(stok_pengaman), 2),
        "kuantitas_pemesanan_ekonomis": round(float(kuantitas_pemesanan_ekonomis), 2),
        "status": status,
        "prioritas": prioritas,
        "tindakan": tindakan,
    }
