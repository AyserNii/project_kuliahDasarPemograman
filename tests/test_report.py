import unittest

from modules.report import buat_laporan_ringkasan_persediaan, format_tabel


class TestLaporan(unittest.TestCase):
    def test_format_tabel_menghasilkan_header_dan_baris(self):
        hasil = format_tabel(["SKU", "Nama"], [["BRG-001", "Kopi"]])

        self.assertIn("SKU", hasil)
        self.assertIn("BRG-001", hasil)
        self.assertIn("Kopi", hasil)

    def test_ringkasan_menggunakan_kolom_persediaan_bahasa_indonesia(self):
        hasil = buat_laporan_ringkasan_persediaan(
            [
                {
                    "sku": "BRG-001",
                    "nama": "Kopi",
                    "jumlah_stok": 2,
                    "biaya_satuan": 1000,
                    "stok_minimum": 5,
                }
            ]
        )

        self.assertIn("BRG-001", hasil)
        self.assertIn("Rp 2,000.00", hasil)


if __name__ == "__main__":
    unittest.main()
