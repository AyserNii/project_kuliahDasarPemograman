import unittest
from modules.inventory import (
    hitung_kuantitas_pemesanan_ekonomis,
    hitung_stok_pengaman,
    hitung_titik_pemesanan_ulang,
    hitung_biaya_persediaan,
)


class TestInventoryCalculations(unittest.TestCase):
    def test_calculate_eoq(self):
        # D = 2400, S = 50000, H = 12000
        # EOQ = sqrt((2 * 2400 * 50000) / 12000) = sqrt(20000) ≈ 141.42
        kuantitas_pemesanan_ekonomis = hitung_kuantitas_pemesanan_ekonomis(2400, 50000, 12000)
        self.assertAlmostEqual(kuantitas_pemesanan_ekonomis, 141.42, places=2)

    def test_calculate_safety_stock(self):
        # Jurnal: usage 9.8 units/day * 2-day lead time, rounded up to whole units.
        stok_pengaman = hitung_stok_pengaman(9.8, 2)
        self.assertEqual(stok_pengaman, 20)

    def test_calculate_reorder_point(self):
        # ROP = (9.8 * 2) + rounded safety stock (20) = 39.6.
        titik_pemesanan_ulang = hitung_titik_pemesanan_ulang(9.8, 2, 20)
        self.assertAlmostEqual(titik_pemesanan_ulang, 39.6, places=2)

    def test_journal_eoq_example(self):
        kuantitas_pemesanan_ekonomis = hitung_kuantitas_pemesanan_ekonomis(
            3057.6, 90000, 8000
        )
        self.assertAlmostEqual(kuantitas_pemesanan_ekonomis, 262.29, places=2)

    def test_invalid_parameters_raise_error(self):
        with self.assertRaises(ValueError):
            hitung_kuantitas_pemesanan_ekonomis(-100, 5000, 200)

        with self.assertRaises(ValueError):
            hitung_stok_pengaman(-2, 5)

        with self.assertRaises(ValueError):
            hitung_titik_pemesanan_ulang(-5, 5, 10)

    def test_inventory_costs(self):
        biaya = hitung_biaya_persediaan(
            permintaan_tahunan=2400,
            kuantitas_pemesanan=141.42,
            biaya_pemesanan=50000,
            biaya_penyimpanan_per_unit_tahun=12000,
        )
        self.assertGreater(biaya["total_biaya"], 0)
        self.assertAlmostEqual(biaya["biaya_pemesanan_tahunan"], biaya["biaya_penyimpanan_tahunan"], delta=100)


if __name__ == "__main__":
    unittest.main()
