import unittest
from datetime import date
from modules.validation import (
    validate_positive_number,
    validate_non_negative_number,
    validate_non_empty_string,
    validate_sku,
    validate_transaction_type,
    validate_date_string,
)


class TestValidation(unittest.TestCase):
    def test_validate_positive_number_valid(self):
        self.assertEqual(validate_positive_number("12.5"), 12.5)
        self.assertEqual(validate_positive_number(100), 100.0)

    def test_validate_positive_number_invalid(self):
        with self.assertRaises(ValueError):
            validate_positive_number(0)
        with self.assertRaises(ValueError):
            validate_positive_number(-5)
        with self.assertRaises(ValueError):
            validate_positive_number("abc")

    def test_validate_non_negative_number(self):
        self.assertEqual(validate_non_negative_number(0), 0.0)
        self.assertEqual(validate_non_negative_number("15"), 15.0)
        with self.assertRaises(ValueError):
            validate_non_negative_number(-1)

    def test_validate_non_empty_string(self):
        self.assertEqual(validate_non_empty_string("  Kopi  "), "Kopi")
        with self.assertRaises(ValueError):
            validate_non_empty_string("")
        with self.assertRaises(ValueError):
            validate_non_empty_string("   ")

    def test_validate_sku(self):
        self.assertEqual(validate_sku("brg-001"), "BRG-001")
        with self.assertRaises(ValueError):
            validate_sku("")
        with self.assertRaises(ValueError):
            validate_sku("A" * 45)

    def test_validate_transaction_type(self):
        self.assertEqual(validate_transaction_type("in"), "IN")
        self.assertEqual(validate_transaction_type("OUT"), "OUT")
        with self.assertRaises(ValueError):
            validate_transaction_type("TRANSFER")

    def test_validate_date_string(self):
        self.assertEqual(validate_date_string("2026-11-19"), date(2026, 11, 19))
        with self.assertRaises(ValueError):
            validate_date_string("19/11/2026")


if __name__ == "__main__":
    unittest.main()
