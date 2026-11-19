from datetime import date, datetime
from typing import Optional, Union


def validasi_angka_positif(nilai: Union[str, int, float], nama_bidang: str = "Nilai") -> float:
    """Validasi bahwa nilai adalah angka dan bernilai lebih besar dari 0 (> 0)."""
    try:
        nilai = float(nilai)
    except (ValueError, TypeError):
        raise ValueError(f"{nama_bidang} harus berupa angka yang valid.")
    if nilai <= 0:
        raise ValueError(f"{nama_bidang} harus bernilai lebih besar dari 0.")
    return nilai


def validasi_angka_tidak_negatif(nilai: Union[str, int, float], nama_bidang: str = "Nilai") -> float:
    """Validasi bahwa nilai adalah angka dan bernilai >= 0."""
    try:
        nilai = float(nilai)
    except (ValueError, TypeError):
        raise ValueError(f"{nama_bidang} harus berupa angka yang valid.")
    if nilai < 0:
        raise ValueError(f"{nama_bidang} tidak boleh bernilai negatif.")
    return nilai


def validasi_teks_tidak_kosong(nilai: Optional[str], nama_bidang: str = "Input") -> str:
    """Validasi bahwa string tidak boleh kosong atau hanya whitespace."""
    if nilai is None or not str(nilai).strip():
        raise ValueError(f"{nama_bidang} tidak boleh kosong.")
    return str(nilai).strip()


def validasi_sku(sku: str) -> str:
    """Validasi format SKU (tidak kosong, alfanumerik / tanda minus / garis bawah)."""
    sku_bersih = validasi_teks_tidak_kosong(sku, "SKU Produk").upper()
    if len(sku_bersih) > 40:
        raise ValueError("SKU tidak boleh lebih dari 40 karakter.")
    return sku_bersih


def validasi_jenis_transaksi(jenis_transaksi: str) -> str:
    """Validasi tipe transaksi hanya boleh 'IN' atau 'OUT'."""
    jenis_bersih = validasi_teks_tidak_kosong(jenis_transaksi, "Tipe transaksi").upper()
    if jenis_bersih not in ("IN", "OUT"):
        raise ValueError("Tipe transaksi harus 'IN' (masuk) atau 'OUT' (keluar).")
    return jenis_bersih


def validasi_teks_tanggal(teks_tanggal: str) -> date:
    """Validasi format tanggal YYYY-MM-DD."""
    bersih = validasi_teks_tidak_kosong(teks_tanggal, "Tanggal")
    try:
        return datetime.strptime(bersih, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD (contoh: 2026-11-19).")
