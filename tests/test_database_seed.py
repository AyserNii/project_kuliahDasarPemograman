import unittest
from collections import defaultdict
from decimal import Decimal

from database.seed import (
    DATA_PRODUK,
    DATA_PENJUALAN,
    DATA_TRANSAKSI,
    _hitung_hasil_analisis,
)


class DatabaseSeedTests(unittest.TestCase):
    def test_sample_product_stocks_match_seed_transactions(self):
        stock_by_sku = defaultdict(Decimal)

        for transaksi in DATA_TRANSAKSI:
            _, sku, _, jenis_transaksi, kuantitas, *_ = transaksi
            movement = Decimal(kuantitas)
            stock_by_sku[sku] += movement if jenis_transaksi == "IN" else -movement

        for produk in DATA_PRODUK:
            sku, _, _, _, _, jumlah_stok, *_ = produk
            self.assertEqual(stock_by_sku[sku], Decimal(jumlah_stok))

    def test_sales_rows_match_outgoing_transactions(self):
        transactions_by_code = {baris[0]: baris for baris in DATA_TRANSAKSI}

        for sale in DATA_PENJUALAN:
            kode_transaksi, sku, kuantitas, *_ = sale
            transaksi = transactions_by_code[kode_transaksi]
            self.assertEqual(transaksi[1], sku)
            self.assertEqual(transaksi[3], "OUT")
            self.assertEqual(Decimal(transaksi[4]), Decimal(kuantitas))

    def test_inventory_analysis_sample_calculation(self):
        self.assertEqual(
            _hitung_hasil_analisis(
                Decimal("2400"),
                Decimal("50000"),
                Decimal("12000"),
                Decimal("8"),
                Decimal("2"),
                Decimal("5"),
                Decimal("1.650"),
            ),
            (Decimal("141.42"), Decimal("7.38"), Decimal("47.38")),
        )


if __name__ == "__main__":
    unittest.main()
