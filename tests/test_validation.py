import unittest
from datetime import date
from modules.validation import (
    validasi_angka_positif,
    validasi_angka_tidak_negatif,
    validasi_teks_tidak_kosong,
    validasi_sku,
    validasi_jenis_transaksi,
    validasi_teks_tanggal,
)


class TestValidation(unittest.TestCase):
    def test_validate_positive_number_valid(self):
        self.assertEqual(validasi_angka_positif("12.5"), 12.5)
        self.assertEqual(validasi_angka_positif(100), 100.0)

    def test_validate_positive_number_invalid(self):
        with self.assertRaises(ValueError):
            validasi_angka_positif(0)
        with self.assertRaises(ValueError):
            validasi_angka_positif(-5)
        with self.assertRaises(ValueError):
            validasi_angka_positif("abc")

    def test_validate_non_negative_number(self):
        self.assertEqual(validasi_angka_tidak_negatif(0), 0.0)
        self.assertEqual(validasi_angka_tidak_negatif("15"), 15.0)
        with self.assertRaises(ValueError):
            validasi_angka_tidak_negatif(-1)

    def test_validate_non_empty_string(self):
        self.assertEqual(validasi_teks_tidak_kosong("  Kopi  "), "Kopi")
        with self.assertRaises(ValueError):
            validasi_teks_tidak_kosong("")
        with self.assertRaises(ValueError):
            validasi_teks_tidak_kosong("   ")

    def test_validate_sku(self):
        self.assertEqual(validasi_sku("brg-001"), "BRG-001")
        with self.assertRaises(ValueError):
            validasi_sku("")
        with self.assertRaises(ValueError):
            validasi_sku("A" * 45)

    def test_validate_transaction_type(self):
        self.assertEqual(validasi_jenis_transaksi("in"), "IN")
        self.assertEqual(validasi_jenis_transaksi("OUT"), "OUT")
        with self.assertRaises(ValueError):
            validasi_jenis_transaksi("TRANSFER")

    def test_validate_date_string(self):
        self.assertEqual(validasi_teks_tanggal("2026-11-19"), date(2026, 11, 19))
        with self.assertRaises(ValueError):
            validasi_teks_tanggal("19/11/2026")


if __name__ == "__main__":
    unittest.main()
