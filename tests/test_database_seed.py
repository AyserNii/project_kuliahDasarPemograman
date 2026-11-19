import unittest
from collections import defaultdict
from decimal import Decimal

from database.seed import (
    PRODUCTS,
    SALES,
    TRANSACTIONS,
    _analysis_results,
)


class DatabaseSeedTests(unittest.TestCase):
    def test_sample_product_stocks_match_seed_transactions(self):
        stock_by_sku = defaultdict(Decimal)

        for transaction in TRANSACTIONS:
            _, sku, _, transaction_type, quantity, *_ = transaction
            movement = Decimal(quantity)
            stock_by_sku[sku] += movement if transaction_type == "IN" else -movement

        for product in PRODUCTS:
            sku, _, _, _, _, stock_quantity, *_ = product
            self.assertEqual(stock_by_sku[sku], Decimal(stock_quantity))

    def test_sales_rows_match_outgoing_transactions(self):
        transactions_by_code = {row[0]: row for row in TRANSACTIONS}

        for sale in SALES:
            transaction_code, sku, quantity, *_ = sale
            transaction = transactions_by_code[transaction_code]
            self.assertEqual(transaction[1], sku)
            self.assertEqual(transaction[3], "OUT")
            self.assertEqual(Decimal(transaction[4]), Decimal(quantity))

    def test_inventory_analysis_sample_calculation(self):
        self.assertEqual(
            _analysis_results(
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
