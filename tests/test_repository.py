import unittest
import uuid
from database.connection import buat_koneksi
from repositories.product_repository import RepositoriProduk
from repositories.supplier_repository import RepositoriPemasok
from repositories.transaction_repository import RepositoriTransaksi
from repositories.sales_repository import RepositoriPenjualan
from repositories.analysis_repository import RepositoriAnalisis


class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.prod_repo = RepositoriProduk()
        self.sup_repo = RepositoriPemasok()
        self.txn_repo = RepositoriTransaksi()
        self.repositori_penjualan = RepositoriPenjualan()
        self.repositori_analisis = RepositoriAnalisis()

    def test_database_connection(self):
        with buat_koneksi() as koneksi:
            self.assertIsNotNone(koneksi)

    def test_supplier_crud(self):
        unique_code = f"TEST-SUP-{uuid.uuid4().hex[:6].upper()}"
        pemasok = self.sup_repo.buat(
            kode_pemasok=unique_code,
            nama="Test Supplier PT",
            nama_kontak="Bambang",
            telepon="081299998888",
            alamat="Surabaya",
        )
        self.assertEqual(pemasok["kode_pemasok"], unique_code)

        fetched = self.sup_repo.ambil_berdasarkan_kode(unique_code)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["nama"], "Test Supplier PT")

        # Cleanup
        self.sup_repo.hapus(pemasok["id_pemasok"])

    def test_product_lifecycle(self):
        unique_sku = f"TEST-BRG-{uuid.uuid4().hex[:6].upper()}"
        produk = self.prod_repo.buat(
            sku=unique_sku,
            nama="Barang Percobaan",
            kategori="Uji Coba",
            satuan="pcs",
            jumlah_stok=50,
            biaya_satuan=10000,
            harga_jual=15000,
            stok_minimum=10,
        )
        self.assertEqual(produk["sku"], unique_sku)
        self.assertEqual(float(produk["jumlah_stok"]), 50.0)

        # Update stok
        updated = self.prod_repo.perbarui_stok(produk["id_produk"], 15)
        self.assertEqual(float(updated["jumlah_stok"]), 65.0)

        # Cleanup
        self.prod_repo.hapus(produk["id_produk"])


if __name__ == "__main__":
    unittest.main()
