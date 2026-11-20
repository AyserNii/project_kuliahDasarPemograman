import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from psycopg.errors import ForeignKeyViolation

from modules.cli_menu import AntarmukaSmartStockCLI


class TestTampilanTabelCLI(unittest.TestCase):
    def buat_aplikasi(self):
        aplikasi = object.__new__(AntarmukaSmartStockCLI)
        aplikasi.tampilkan_produk = lambda: None
        aplikasi.repositori_produk = SimpleNamespace(
            ambil_berdasarkan_id=lambda id_produk: {
                "id_produk": id_produk,
                "nama": "Kopi",
                "sku": "BRG-001",
            }
        )
        return aplikasi

    def test_hasil_analisis_dicetak_dalam_tabel(self):
        aplikasi = self.buat_aplikasi()
        aplikasi.layanan_persediaan = SimpleNamespace(
            analisis_produk=lambda **kwargs: {
                "analisis": {
                    "permintaan_tahunan": 100,
                    "biaya_pemesanan": 50_000,
                    "biaya_penyimpanan_per_unit_tahun": 1_000,
                    "kuantitas_pemesanan_ekonomis": 100,
                    "stok_pengaman": 10,
                    "titik_pemesanan_ulang": 20,
                },
                "rekomendasi": {
                    "status": "AMAN",
                    "stok_saat_ini": 50,
                    "tindakan": "Stok masih mencukupi.",
                },
                "biaya": {
                    "jumlah_pemesanan_per_tahun": 1,
                    "hari_siklus_pemesanan": 365,
                    "total_biaya": 1_000,
                },
            }
        )
        keluaran = StringIO()

        with patch("builtins.input", side_effect=["1", "", "", "", "", ""]):
            with patch("modules.cli_menu.cetak_judul"), redirect_stdout(keluaran):
                aplikasi.jalankan_analisis_satu_produk()

        self.assertIn("HASIL ANALISIS PERSEDIAAN", keluaran.getvalue())
        self.assertIn("Kuantitas Pesan Ekonomis (EOQ)", keluaran.getvalue())
        self.assertIn("Rekomendasi:", keluaran.getvalue())
        self.assertIn("+-", keluaran.getvalue())

    def test_hasil_peramalan_dicetak_dalam_tabel(self):
        aplikasi = self.buat_aplikasi()
        aplikasi.repositori_penjualan = SimpleNamespace(
            ambil_penjualan_harian=lambda id_produk, hari: [
                {"total_kuantitas": 2},
                {"total_kuantitas": 3},
                {"total_kuantitas": 4},
            ]
        )
        keluaran = StringIO()

        with patch("builtins.input", return_value="1"):
            with patch("modules.cli_menu.cetak_judul"), redirect_stdout(keluaran):
                aplikasi.menu_peramalan()

        self.assertIn("HASIL PERAMALAN PERMINTAAN", keluaran.getvalue())
        self.assertIn("Rata-rata Bergerak (3 periode)", keluaran.getvalue())
        self.assertIn("+-", keluaran.getvalue())

    def test_hapus_produk_menampilkan_pesan_jika_masih_direferensikan(self):
        aplikasi = self.buat_aplikasi()

        def gagal_hapus(id_produk):
            raise ForeignKeyViolation("produk masih direferensikan")

        aplikasi.repositori_produk.hapus = gagal_hapus
        keluaran = StringIO()

        with patch("builtins.input", side_effect=["1", "y"]):
            with patch("modules.cli_menu.cetak_judul"), redirect_stdout(keluaran):
                aplikasi.hapus_produk()

        self.assertIn("masih digunakan dalam transaksi atau analisis inventaris", keluaran.getvalue())
        self.assertNotIn("violates RESTRICT", keluaran.getvalue())


if __name__ == "__main__":
    unittest.main()
