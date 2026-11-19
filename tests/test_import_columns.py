import csv
import tempfile
import unittest
from pathlib import Path

from services.import_service import LayananImpor


class RepositoriProdukPalsu:
    def __init__(self):
        self.data_tersimpan = None

    def ambil_berdasarkan_sku(self, sku):
        return None

    def buat(self, **data_produk):
        self.data_tersimpan = data_produk
        return data_produk


class RepositoriPemasokPalsu:
    def ambil_berdasarkan_kode(self, kode_pemasok):
        return None


class TestKolomImporLama(unittest.TestCase):
    def test_import_menerima_nama_kolom_csv_lama(self):
        repositori_produk = RepositoriProdukPalsu()
        layanan = LayananImpor(
            repositori_produk=repositori_produk,
            repositori_pemasok=RepositoriPemasokPalsu(),
        )

        with tempfile.TemporaryDirectory() as direktori:
            jalur_csv = Path(direktori) / "produk.csv"
            with jalur_csv.open("w", newline="", encoding="utf-8") as berkas:
                penulis = csv.writer(berkas)
                penulis.writerow(
                    [
                        "sku",
                        "name",
                        "category",
                        "supplier_code",
                        "unit",
                        "stock_quantity",
                        "unit_cost",
                        "selling_price",
                        "minimum_stock",
                    ]
                )
                penulis.writerow(
                    ["BRG-OLD", "Produk Lama", "Minuman", "", "pcs", "4", "10", "15", "1"]
                )

            berhasil, gagal, _ = layanan.impor_produk_dari_csv(jalur_csv)

        self.assertEqual((berhasil, gagal), (1, 0))
        self.assertEqual(repositori_produk.data_tersimpan["nama"], "Produk Lama")
        self.assertEqual(repositori_produk.data_tersimpan["satuan"], "pcs")


if __name__ == "__main__":
    unittest.main()
