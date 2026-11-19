from datetime import date, datetime
from typing import Optional, Union


def validate_positive_number(value: Union[str, int, float], field_name: str = "Nilai") -> float:
    """Validasi bahwa nilai adalah angka dan bernilai lebih besar dari 0 (> 0)."""
    try:
        val = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} harus berupa angka yang valid.")
    if val <= 0:
        raise ValueError(f"{field_name} harus bernilai lebih besar dari 0.")
    return val


def validate_non_negative_number(value: Union[str, int, float], field_name: str = "Nilai") -> float:
    """Validasi bahwa nilai adalah angka dan bernilai >= 0."""
    try:
        val = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} harus berupa angka yang valid.")
    if val < 0:
        raise ValueError(f"{field_name} tidak boleh bernilai negatif.")
    return val


def validate_non_empty_string(value: Optional[str], field_name: str = "Input") -> str:
    """Validasi bahwa string tidak boleh kosong atau hanya whitespace."""
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} tidak boleh kosong.")
    return str(value).strip()


def validate_sku(sku: str) -> str:
    """Validasi format SKU (tidak kosong, alfanumerik / tanda minus / garis bawah)."""
    clean_sku = validate_non_empty_string(sku, "SKU Produk").upper()
    if len(clean_sku) > 40:
        raise ValueError("SKU tidak boleh lebih dari 40 karakter.")
    return clean_sku


def validate_transaction_type(txn_type: str) -> str:
    """Validasi tipe transaksi hanya boleh 'IN' atau 'OUT'."""
    clean_type = validate_non_empty_string(txn_type, "Tipe transaksi").upper()
    if clean_type not in ("IN", "OUT"):
        raise ValueError("Tipe transaksi harus 'IN' (masuk) atau 'OUT' (keluar).")
    return clean_type


def validate_date_string(date_str: str) -> date:
    """Validasi format tanggal YYYY-MM-DD."""
    clean = validate_non_empty_string(date_str, "Tanggal")
    try:
        return datetime.strptime(clean, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD (contoh: 2026-11-19).")
