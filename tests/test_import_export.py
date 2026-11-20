import csv
import tempfile
import unittest
import uuid
from pathlib import Path

from repositories.product_repository import RepositoriProduk
from repositories.supplier_repository import RepositoriPemasok
from services.export_service import LayananEkspor
from services.import_service import LayananImpor


class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.prod_repo = RepositoriProduk()
        self.sup_repo = RepositoriPemasok()
        self.layanan_impor = LayananImpor(self.prod_repo, self.sup_repo)
        self.layanan_ekspor = LayananEkspor(self.prod_repo)

    def test_export_products_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_products_export.csv"
            result_path = self.layanan_ekspor.ekspor_produk_ke_csv(jalur_keluaran=out_file)
            self.assertTrue(result_path.exists())

            with open(result_path, mode="r", encoding="utf-8-sig") as berkas:
                reader = csv.reader(berkas, delimiter=";")
                header = next(reader)
                self.assertIn("sku", header)
                self.assertIn("nama", header)

    def test_import_products_from_csv(self):
        unique_sku = f"IMP-{uuid.uuid4().hex[:6].upper()}"
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test_import.csv"
            with open(csv_file, mode="w", newline="", encoding="utf-8") as berkas:
                writer = csv.writer(berkas)
                writer.writerow([
                    "sku", "nama", "kategori", "kode_pemasok", "satuan",
                    "jumlah_stok", "biaya_satuan", "harga_jual", "stok_minimum"
                ])
                writer.writerow([
                    unique_sku, "Produk Import Test", "Kategori Test", "", "box",
                    "30", "12000", "18000", "5"
                ])

            berhasil, gagal, daftar_kesalahan = self.layanan_impor.impor_produk_dari_csv(csv_file)
            self.assertEqual(berhasil, 1)
            self.assertEqual(gagal, 0)

            # Verifikasi di database
            saved = self.prod_repo.ambil_berdasarkan_sku(unique_sku)
            self.assertIsNotNone(saved)
            self.assertEqual(saved["nama"], "Produk Import Test")

            # Cleanup
            self.prod_repo.hapus(saved["id_produk"])


if __name__ == "__main__":
    unittest.main()
