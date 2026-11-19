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
        # stddev = 2, L = 5, Z = 1.650
        # SS = 1.650 * 2 * sqrt(5) ≈ 7.38
        stok_pengaman = hitung_stok_pengaman(2, 5, 1.650)
        self.assertAlmostEqual(stok_pengaman, 7.38, places=2)

    def test_calculate_reorder_point(self):
        # avg_d = 8, L = 5, SS = 7.38
        # ROP = (8 * 5) + 7.38 = 47.38
        titik_pemesanan_ulang = hitung_titik_pemesanan_ulang(8, 5, 7.38)
        self.assertAlmostEqual(titik_pemesanan_ulang, 47.38, places=2)

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
