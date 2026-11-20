from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import DIREKTORI_GRAFIK_KELUARAN, DIREKTORI_LAPORAN_KELUARAN
import pandas as pd


def ubah_dataframe_ke_tabel_teks(kerangka_data: pd.DataFrame) -> str:
    """Mengubah Pandas DataFrame menjadi format tabel teks yang rapi untuk CLI."""
    if kerangka_data.empty:
        return "Tidak ada data (DataFrame kosong)."
    return kerangka_data.to_string(index=False)


def format_tabel(judul_kolom: List[str], baris_data: List[List[Any]]) -> str:
    """Membuat tabel teks ASCII yang rapi untuk CLI."""
    if not judul_kolom:
        return ""

    baris_terformat = [
        [str(elemen) if elemen is not None else "" for elemen in baris]
        for baris in baris_data
    ]
    lebar_kolom = [len(judul) for judul in judul_kolom]

    for baris in baris_terformat:
        for indeks, nilai in enumerate(baris):
            if indeks < len(lebar_kolom):
                lebar_kolom[indeks] = max(lebar_kolom[indeks], len(nilai))

    pemisah = "+-" + "-+-".join("-" * lebar for lebar in lebar_kolom) + "-+"
    baris_judul = "| " + " | ".join(
        judul.ljust(lebar_kolom[indeks])
        for indeks, judul in enumerate(judul_kolom)
    ) + " |"

    keluaran = [pemisah, baris_judul, pemisah]
    for baris in baris_terformat:
        teks_baris = "| " + " | ".join(
            nilai.ljust(lebar_kolom[indeks])
            for indeks, nilai in enumerate(baris)
        ) + " |"
        keluaran.append(teks_baris)
    keluaran.append(pemisah)

    return "\n".join(keluaran)


def buat_laporan_ringkasan_persediaan(
    daftar_produk: List[Dict[str, Any]],
) -> str:
    """Menghasilkan teks ringkasan inventaris."""
    jumlah_jenis_produk = len(daftar_produk)
    total_kuantitas = sum(
        float(produk.get("jumlah_stok", 0)) for produk in daftar_produk
    )
    total_nilai_aset = sum(
        float(produk.get("jumlah_stok", 0))
        * float(produk.get("biaya_satuan", 0))
        for produk in daftar_produk
    )
    produk_stok_menipis = [
        produk
        for produk in daftar_produk
        if float(produk.get("jumlah_stok", 0))
        <= float(produk.get("stok_minimum", 0))
    ]

    baris_laporan = [
        "=" * 60,
        "             RINGKASAN STATUS INVENTARIS",
        f"        Waktu Pembuatan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        f"Total Jenis Produk      : {jumlah_jenis_produk}",
        f"Total Kuantitas Fisik   : {total_kuantitas:,.2f} unit",
        f"Total Nilai Aset Stok   : Rp {total_nilai_aset:,.2f}",
        f"Jumlah Produk Menipis   : {len(produk_stok_menipis)} item",
        "-" * 60,
    ]

    if produk_stok_menipis:
        baris_laporan.append(
            "\n[PERINGATAN] Produk yang Mencapai/Di Bawah Batas Minimum:"
        )
        judul_kolom = ["SKU", "Nama Produk", "Stok Saat Ini", "Min. Stok"]
        baris_data = [
            [
                produk["sku"],
                produk["nama"][:25],
                f"{float(produk['jumlah_stok']):.2f}",
                f"{float(produk['stok_minimum']):.2f}",
            ]
            for produk in produk_stok_menipis
        ]
        baris_laporan.append(format_tabel(judul_kolom, baris_data))

    return "\n".join(baris_laporan)


def simpan_laporan_teks(
    isi: str, awalan_nama_berkas: str = "laporan"
) -> Path:
    """Menyimpan laporan teks ke direktori output/reports/."""
    cap_waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_berkas = f"{awalan_nama_berkas}_{cap_waktu}.txt"
    jalur_berkas = DIREKTORI_LAPORAN_KELUARAN / nama_berkas
    jalur_berkas.write_text(isi, encoding="utf-8")
    return jalur_berkas


def buat_grafik_stok(
    daftar_produk: List[Dict[str, Any]],
    nama_berkas: str = "stok_barang.png",
) -> Optional[Path]:
    """
    Membuat grafik stok barang jika matplotlib tersedia.
    """
    try:
        import matplotlib.pyplot as plt

        nama_produk = [produk["nama"][:15] for produk in daftar_produk[:15]]
        stok_produk = [
            float(produk.get("jumlah_stok", 0))
            for produk in daftar_produk[:15]
        ]

        plt.figure(figsize=(10, 6))
        plt.barh(nama_produk, stok_produk, color="skyblue")
        plt.xlabel("Jumlah Stok (Unit)")
        plt.ylabel("Produk")
        plt.title("Tingkat Stok Produk SmartStock")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        jalur_keluaran = DIREKTORI_GRAFIK_KELUARAN / nama_berkas
        plt.savefig(jalur_keluaran)
        plt.close()
        return jalur_keluaran
    except ImportError:
        return None


def grafik_batang_ascii(judul: str, daftar_item: List[tuple]) -> str:
    """Membuat visualisasi grafik batang sederhana berbasis karakter ASCII."""
    if not daftar_item:
        return "Tidak ada data untuk ditampilkan."

    nilai_maksimum = max((nilai for _, nilai in daftar_item), default=1)
    nilai_maksimum = max(nilai_maksimum, 1)
    panjang_label_maksimum = max(
        (len(str(label)) for label, _ in daftar_item), default=10
    )
    lebar_batang = 35

    baris_teks = [f"\n--- {judul} ---"]
    for label, nilai in daftar_item:
        jumlah_karakter = int((float(nilai) / nilai_maksimum) * lebar_batang)
        batang = "#" * jumlah_karakter
        baris_teks.append(
            f"{str(label).ljust(panjang_label_maksimum)} | {batang} ({nilai:.1f})"
        )

    return "\n".join(baris_teks)


# Alias Kompatibilitas
hasilkan_laporan_ringkasan_inventaris = buat_laporan_ringkasan_persediaan
generate_inventory_summary_report = buat_laporan_ringkasan_persediaan
hasilkan_grafik_stok = buat_grafik_stok
generate_stock_chart = buat_grafik_stok
save_text_report = simpan_laporan_teks
format_table = format_tabel
ascii_bar_chart = grafik_batang_ascii
dataframe_to_string_table = ubah_dataframe_ke_tabel_teks
