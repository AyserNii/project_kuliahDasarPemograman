import csv
import tempfile
import unittest
from pathlib import Path

from services.export_service import LayananEkspor


class RepositoriProdukPalsu:
    def ambil_semua(self):
        return [{"sku": "BRG-001", "nama": "Kopi"}]


class TestEksporCsvExcel(unittest.TestCase):
    def test_ekspor_produk_memakai_pemisah_dan_encoding_excel(self):
        layanan = LayananEkspor(repositori_produk=RepositoriProdukPalsu())

        with tempfile.TemporaryDirectory() as direktori:
            jalur_csv = layanan.ekspor_produk_ke_csv(Path(direktori) / "produk.csv")

            with jalur_csv.open(encoding="utf-8-sig", newline="") as berkas:
                baris = list(csv.reader(berkas, delimiter=";"))

        self.assertEqual(baris[0], ["sku", "nama"])
        self.assertEqual(baris[1], ["BRG-001", "Kopi"])


if __name__ == "__main__":
    unittest.main()
