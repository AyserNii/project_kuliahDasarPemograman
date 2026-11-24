import unittest
from datetime import date

from modules.forecasting import buat_peramalan_regresi_linear


class TestPeramalan(unittest.TestCase):
    def test_least_squares_forecasts_next_three_annual_periods(self):
        data_tahunan = [
            {"tahun": 2018, "total_kuantitas": 1},
            {"tahun": 2019, "total_kuantitas": 2},
            {"tahun": 2020, "total_kuantitas": 3},
        ]

        hasil = buat_peramalan_regresi_linear(
            data_tahunan,
            tanggal_acuan=date(2020, 12, 26),
        )

        self.assertAlmostEqual(hasil["intersep"], 0)
        self.assertAlmostEqual(hasil["kemiringan"], 1)
        self.assertEqual(
            [baris["permintaan_tahunan"] for baris in hasil["ramalan"]],
            [4.0, 5.0, 6.0],
        )
        self.assertEqual(
            [baris["tahun"] for baris in hasil["ramalan"]],
            [2021, 2022, 2023],
        )

    def test_journal_history_uses_calculated_least_squares_not_printed_coefficients(self):
        data_tahunan = [
            {"tahun": 2013, "total_kuantitas": 1700},
            {"tahun": 2014, "total_kuantitas": 2284},
            {"tahun": 2015, "total_kuantitas": 2920},
            {"tahun": 2016, "total_kuantitas": 3300},
            {"tahun": 2017, "total_kuantitas": 3000},
        ]

        hasil = buat_peramalan_regresi_linear(
            data_tahunan,
            tanggal_acuan=date(2017, 12, 26),
        )

        self.assertAlmostEqual(hasil["intersep"], 1556.0)
        self.assertAlmostEqual(hasil["kemiringan"], 361.6)
        self.assertEqual(
            [baris["permintaan_tahunan"] for baris in hasil["ramalan"]],
            [3725.6, 4087.2, 4448.8],
        )

    def test_current_year_demand_is_annualized_using_journal_workday_basis(self):
        hasil = buat_peramalan_regresi_linear(
            [{"tahun": 2024, "total_kuantitas": 100}],
            jumlah_periode=1,
            tanggal_acuan=date(2024, 6, 26),
        )

        self.assertEqual(hasil["historis"][0]["permintaan_tahunan"], 200.0)
        self.assertEqual(hasil["ramalan"][0]["permintaan_tahunan"], 200.0)

    def test_empty_history_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Riwayat permintaan tahunan"):
            buat_peramalan_regresi_linear([])


if __name__ == "__main__":
    unittest.main()
