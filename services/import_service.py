from pathlib import Path
from typing import List, Tuple
import pandas as pd

from config.settings import DIREKTORI_IMPOR
from repositories.product_repository import RepositoriProduk
from repositories.supplier_repository import RepositoriPemasok


def _normalkan_kolom_csv_lama(kerangka_data: pd.DataFrame) -> pd.DataFrame:
    """Menerima nama kolom CSV lama sambil menormalkannya ke bahasa Indonesia."""
    pemetaan_kolom = {
        "name": "nama",
        "category": "kategori",
        "supplier_code": "kode_pemasok",
        "contact_name": "nama_kontak",
        "phone": "telepon",
        "address": "alamat",
        "unit": "satuan",
        "stock_quantity": "jumlah_stok",
        "unit_cost": "biaya_satuan",
        "selling_price": "harga_jual",
        "minimum_stock": "stok_minimum",
    }
    perubahan = {
        kolom_lama: kolom_baru
        for kolom_lama, kolom_baru in pemetaan_kolom.items()
        if kolom_lama in kerangka_data.columns
        and kolom_baru not in kerangka_data.columns
    }
    return kerangka_data.rename(columns=perubahan)


class LayananImpor:
    """
    Service untuk membaca file CSV menggunakan library Pandas (pd.read_csv)
    dan menyimpannya ke database PostgreSQL.
    """

    def __init__(
        self,
        repositori_produk: RepositoriProduk = None,
        repositori_pemasok: RepositoriPemasok = None,
    ):
        self.repositori_produk = repositori_produk or RepositoriProduk()
        self.repositori_pemasok = repositori_pemasok or RepositoriPemasok()

    def impor_pemasok_dari_csv(self, jalur_berkas: Path) -> Tuple[int, int, List[str]]:
        """
        Import data pemasok dari file CSV menggunakan Pandas DataFrame.
        Format kolom: kode_pemasok, nama, nama_kontak, telepon, alamat
        """
        if not jalur_berkas.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {jalur_berkas}")

        # Membaca data CSV ke dalam Pandas DataFrame
        kerangka_data = _normalkan_kolom_csv_lama(
            pd.read_csv(
                jalur_berkas, sep=None, engine="python", dtype=str, encoding="utf-8-sig"
            ).fillna("")
        )

        jumlah_berhasil = 0
        jumlah_gagal = 0
        daftar_kesalahan = []

        for indeks, baris in kerangka_data.iterrows():
            nomor_baris = indeks + 2  # Nomor baris pada file CSV (termasuk header)
            try:
                kode = str(baris.get("kode_pemasok", "")).strip().upper()
                nama = str(baris.get("nama", "")).strip()

                if not kode or not nama:
                    raise ValueError("kode_pemasok dan nama wajib diisi")

                data_tersedia = self.repositori_pemasok.ambil_berdasarkan_kode(kode)
                if data_tersedia:
                    daftar_kesalahan.append(f"Baris {nomor_baris}: Supplier dengan kode {kode} sudah terdaftar.")
                    jumlah_gagal += 1
                    continue

                kontak = str(baris.get("nama_kontak", "")).strip() or None
                telepon = str(baris.get("telepon", "")).strip() or None
                alamat = str(baris.get("alamat", "")).strip() or None

                self.repositori_pemasok.buat(
                    kode_pemasok=kode,
                    nama=nama,
                    nama_kontak=kontak,
                    telepon=telepon,
                    alamat=alamat,
                )
                jumlah_berhasil += 1
            except Exception as kesalahan:
                jumlah_gagal += 1
                daftar_kesalahan.append(f"Baris {nomor_baris}: {kesalahan}")

        return jumlah_berhasil, jumlah_gagal, daftar_kesalahan

    def impor_produk_dari_csv(self, jalur_berkas: Path) -> Tuple[int, int, List[str]]:
        """
        Import data produk dari file CSV menggunakan Pandas DataFrame.
        Format kolom: sku, nama, kategori, kode_pemasok, satuan, jumlah_stok, biaya_satuan, harga_jual, stok_minimum
        """
        if not jalur_berkas.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {jalur_berkas}")

        # Membaca data CSV ke dalam Pandas DataFrame
        kerangka_data = _normalkan_kolom_csv_lama(
            pd.read_csv(
                jalur_berkas, sep=None, engine="python", dtype=str, encoding="utf-8-sig"
            ).fillna("")
        )

        jumlah_berhasil = 0
        jumlah_gagal = 0
        daftar_kesalahan = []

        for indeks, baris in kerangka_data.iterrows():
            nomor_baris = indeks + 2
            try:
                sku = str(baris.get("sku", "")).strip().upper()
                nama = str(baris.get("nama", "")).strip()

                if not sku or not nama:
                    raise ValueError("sku dan nama wajib diisi")

                data_tersedia = self.repositori_produk.ambil_berdasarkan_sku(sku)
                if data_tersedia:
                    daftar_kesalahan.append(f"Baris {nomor_baris}: Produk dengan SKU {sku} sudah terdaftar.")
                    jumlah_gagal += 1
                    continue

                # Pencocokan supplier
                id_pemasok = None
                kode_pemasok = str(baris.get("kode_pemasok", "")).strip().upper()
                if kode_pemasok:
                    pemasok = self.repositori_pemasok.ambil_berdasarkan_kode(kode_pemasok)
                    if pemasok:
                        id_pemasok = pemasok["id_pemasok"]

                satuan = str(baris.get("satuan", "")).strip() or "pcs"
                stok = float(baris.get("jumlah_stok", 0) or 0)
                biaya = float(baris.get("biaya_satuan", 0) or 0)
                harga = float(baris.get("harga_jual", 0) or 0)
                stok_minimum = float(baris.get("stok_minimum", 0) or 0)

                self.repositori_produk.buat(
                    sku=sku,
                    nama=nama,
                    kategori=str(baris.get("kategori", "")).strip() or None,
                    id_pemasok=id_pemasok,
                    satuan=satuan,
                    jumlah_stok=stok,
                    biaya_satuan=biaya,
                    harga_jual=harga,
                    stok_minimum=stok_minimum,
                )
                jumlah_berhasil += 1
            except Exception as kesalahan:
                jumlah_gagal += 1
                daftar_kesalahan.append(f"Baris {nomor_baris}: {kesalahan}")

        return jumlah_berhasil, jumlah_gagal, daftar_kesalahan

    def buat_template_contoh(self):
        """Membuat template CSV di storage/imports/ menggunakan Pandas."""
        data_produk = {
            "sku": ["BRG-003", "BRG-004"],
            "nama": ["Susu Bubuk 500g", "Sirup Karamel 750ml"],
            "kategori": ["Bahan Minuman", "Bahan Minuman"],
            "kode_pemasok": ["SUP-001", "SUP-001"],
            "satuan": ["pcs", "botol"],
            "jumlah_stok": [50, 30],
            "biaya_satuan": [25000, 45000],
            "harga_jual": [32000, 58000],
            "stok_minimum": [10, 8],
        }
        kerangka_produk = pd.DataFrame(data_produk)
        kerangka_produk.to_csv(
            DIREKTORI_IMPOR / "template_products.csv",
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )

        data_pemasok = {
            "kode_pemasok": ["SUP-002"],
            "nama": ["Distributor Bahan Baku Sejahtera"],
            "nama_kontak": ["Budi Santoso"],
            "telepon": ["081234567890"],
            "alamat": ["Bandung"],
        }
        kerangka_pemasok = pd.DataFrame(data_pemasok)
        kerangka_pemasok.to_csv(
            DIREKTORI_IMPOR / "template_suppliers.csv",
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )
