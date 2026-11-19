import unittest

from modules.forecasting import (
    hitung_statistik_permintaan,
    peramalan_rata_rata_bergerak_pandas,
    rata_rata_bergerak,
)


class TestPeramalan(unittest.TestCase):
    def test_rata_rata_bergerak_menggunakan_jendela_terakhir(self):
        self.assertEqual(rata_rata_bergerak([1, 2, 3], ukuran_jendela=2), 2.5)

    def test_peramalan_pandas_menghasilkan_deret_bergerak(self):
        self.assertEqual(
            peramalan_rata_rata_bergerak_pandas([1, 2, 3], ukuran_jendela=2),
            [None, 1.5, 2.5],
        )

    def test_statistik_permintaan_menggunakan_kunci_bahasa_indonesia(self):
        statistik = hitung_statistik_permintaan([1, 3])
        self.assertEqual(statistik["rata_rata_permintaan_harian"], 2.0)
        self.assertEqual(statistik["permintaan_tahunan"], 730.0)


if __name__ == "__main__":
    unittest.main()
