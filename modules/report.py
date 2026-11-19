from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import OUTPUT_CHARTS_DIR, OUTPUT_REPORTS_DIR
import pandas as pd


def dataframe_to_string_table(df: pd.DataFrame) -> str:
    """Mengubah Pandas DataFrame menjadi format tabel teks yang rapi untuk CLI."""
    if df.empty:
        return "Tidak ada data (DataFrame kosong)."
    return df.to_string(index=False)



def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Membuat tabel teks ASCII yang rapi untuk CLI."""
    if not headers:
        return ""

    str_rows = [[str(item) if item is not None else "" for item in row] for row in rows]
    col_widths = [len(h) for h in headers]

    for row in str_rows:
        for idx, val in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(val))

    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    lines = [separator, header_line, separator]
    for row in str_rows:
        row_line = "| " + " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row)) + " |"
        lines.append(row_line)
    lines.append(separator)

    return "\n".join(lines)


def generate_inventory_summary_report(products: List[Dict[str, Any]]) -> str:
    """Menghasilkan teks ringkasan inventaris."""
    total_items = len(products)
    total_qty = sum(float(p.get("stock_quantity", 0)) for p in products)
    total_asset_value = sum(
        float(p.get("stock_quantity", 0)) * float(p.get("unit_cost", 0)) for p in products
    )
    low_stock_items = [
        p for p in products if float(p.get("stock_quantity", 0)) <= float(p.get("minimum_stock", 0))
    ]

    report_lines = [
        "=" * 60,
        "             RINGKASAN STATUS INVENTARIS",
        f"        Waktu Pembuatan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        f"Total Jenis Produk      : {total_items}",
        f"Total Kuantitas Fisik   : {total_qty:,.2f} unit",
        f"Total Nilai Aset Stok   : Rp {total_asset_value:,.2f}",
        f"Jumlah Produk Menipis   : {len(low_stock_items)} item",
        "-" * 60,
    ]

    if low_stock_items:
        report_lines.append("\n[PERINGATAN] Produk yang Mencapai/Di Bawah Batas Minimum:")
        headers = ["SKU", "Nama Produk", "Stok Saat Ini", "Min. Stok"]
        rows = [
            [
                p["sku"],
                p["name"][:25],
                f"{float(p['stock_quantity']):.2f}",
                f"{float(p['minimum_stock']):.2f}",
            ]
            for p in low_stock_items
        ]
        report_lines.append(format_table(headers, rows))

    return "\n".join(report_lines)


def save_text_report(content: str, filename_prefix: str = "laporan") -> Path:
    """Menyimpan laporan teks ke direktori output/reports/."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.txt"
    filepath = OUTPUT_REPORTS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def generate_stock_chart(products: List[Dict[str, Any]], filename: str = "stok_barang.png") -> Optional[Path]:
    """
    Membuat grafik stok barang.
    Jika library matplotlib terpasang, akan dibuat gambar grafik PNG.
    Jika tidak, fungsi mengembalikan None dan visualisasi ASCII digunakan di CLI.
    """
    try:
        import matplotlib.pyplot as plt

        names = [p["name"][:15] for p in products[:15]]
        stocks = [float(p.get("stock_quantity", 0)) for p in products[:15]]

        plt.figure(figsize=(10, 6))
        bars = plt.barh(names, stocks, color="skyblue")
        plt.xlabel("Jumlah Stok (Unit)")
        plt.ylabel("Produk")
        plt.title("Tingkat Stok Produk SmartStock")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        out_path = OUTPUT_CHARTS_DIR / filename
        plt.savefig(out_path)
        plt.close()
        return out_path
    except ImportError:
        return None


def ascii_bar_chart(title: str, items: List[tuple]) -> str:
    """Membuat visualisasi grafik batang sederhana berbasis karakter ASCII."""
    if not items:
        return "Tidak ada data untuk ditampilkan."

    max_val = max((val for _, val in items), default=1)
    max_val = max(max_val, 1)
    max_label_len = max((len(str(label)) for label, _ in items), default=10)
    bar_width = 35

    lines = [f"\n--- {title} ---"]
    for label, val in items:
        num_chars = int((float(val) / max_val) * bar_width)
        bar = "#" * num_chars
        lines.append(f"{str(label).ljust(max_label_len)} | {bar} ({val:.1f})")

    return "\n".join(lines)
