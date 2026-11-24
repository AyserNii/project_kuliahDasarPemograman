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
        aplikasi.repositori_penjualan = SimpleNamespace(
            ambil_permintaan_tahunan=lambda id_produk: [
                {"tahun": 2024, "total_kuantitas": 100},
                {"tahun": 2025, "total_kuantitas": 120},
                {"tahun": 2026, "total_kuantitas": 140},
            ]
        )
        return aplikasi

    def test_hasil_analisis_dicetak_dalam_tabel(self):
        aplikasi = self.buat_aplikasi()
        aplikasi.layanan_persediaan = SimpleNamespace(
            analisis_produk=lambda **kwargs: {
                "rekomendasi": {
                    "status": "AMAN",
                    "stok_saat_ini": 50,
                    "tindakan": "Stok masih mencukupi.",
                },
                "peramalan": {"persamaan": "y = 100.0 + 1.0x"},
                "proyeksi": [
                    {
                        "tahun": 2027,
                        "permintaan_tahunan": 100.0,
                        "kuantitas_pemesanan_ekonomis": 100.0,
                        "jumlah_pemesanan_per_tahun": 1.0,
                        "stok_pengaman": 10.0,
                        "titik_pemesanan_ulang": 20.0,
                    }
                ],
            }
        )
        keluaran = StringIO()

        with patch("builtins.input", side_effect=["1", "", "", ""]):
            with patch("modules.cli_menu.cetak_judul"), redirect_stdout(keluaran):
                aplikasi.jalankan_analisis_satu_produk()

        self.assertIn("HASIL ANALISIS PERSEDIAAN", keluaran.getvalue())
        self.assertIn("Kuantitas Pesan Ekonomis (EOQ)", keluaran.getvalue())
        self.assertIn("Rekomendasi:", keluaran.getvalue())
        self.assertIn("+-", keluaran.getvalue())

    def test_hasil_peramalan_dicetak_dalam_tabel(self):
        aplikasi = self.buat_aplikasi()
        keluaran = StringIO()

        with patch("builtins.input", return_value="1"):
            with patch("modules.cli_menu.cetak_judul"), redirect_stdout(keluaran):
                aplikasi.menu_peramalan()

        self.assertIn("HASIL PERAMALAN PERMINTAAN", keluaran.getvalue())
        self.assertIn("Least Squares", keluaran.getvalue())
        self.assertIn("Peramalan", keluaran.getvalue())
        self.assertIn("+-", keluaran.getvalue())

    def test_analisis_massal_mencetak_proyeksi_tiga_tahun(self):
        aplikasi = self.buat_aplikasi()
        aplikasi.layanan_persediaan = SimpleNamespace(
            analisis_semua_produk=lambda: [
                {
                    "produk": {"nama": "Kopi", "sku": "BRG-001"},
                    "peramalan": {"persamaan": "y = 100.0 + 1.0x"},
                    "proyeksi": [
                        {
                            "tahun": tahun,
                            "permintaan_tahunan": 100.0,
                            "kuantitas_pemesanan_ekonomis": 10.0,
                            "jumlah_pemesanan_per_tahun": 10.0,
                            "stok_pengaman": 1.0,
                            "titik_pemesanan_ulang": 2.0,
                        }
                        for tahun in (2027, 2028, 2029)
                    ],
                }
            ]
        )
        keluaran = StringIO()

        with redirect_stdout(keluaran):
            aplikasi.jalankan_analisis_massal()

        self.assertIn("2027", keluaran.getvalue())
        self.assertIn("2028", keluaran.getvalue())
        self.assertIn("2029", keluaran.getvalue())
        self.assertIn("Garis regresi permintaan", keluaran.getvalue())

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
