import csv
import tempfile
import unittest
import uuid
from pathlib import Path

from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository
from services.export_service import ExportService
from services.import_service import ImportService


class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.prod_repo = ProductRepository()
        self.sup_repo = SupplierRepository()
        self.import_service = ImportService(self.prod_repo, self.sup_repo)
        self.export_service = ExportService(self.prod_repo)

    def test_export_products_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_products_export.csv"
            result_path = self.export_service.export_products_csv(output_path=out_file)
            self.assertTrue(result_path.exists())

            with open(result_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertIn("sku", header)
                self.assertIn("name", header)

    def test_import_products_from_csv(self):
        unique_sku = f"IMP-{uuid.uuid4().hex[:6].upper()}"
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test_import.csv"
            with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "sku", "name", "category", "supplier_code", "unit",
                    "stock_quantity", "unit_cost", "selling_price", "minimum_stock"
                ])
                writer.writerow([
                    unique_sku, "Produk Import Test", "Kategori Test", "", "box",
                    "30", "12000", "18000", "5"
                ])

            success, fail, errors = self.import_service.import_products_from_csv(csv_file)
            self.assertEqual(success, 1)
            self.assertEqual(fail, 0)

            # Verifikasi di database
            saved = self.prod_repo.get_by_sku(unique_sku)
            self.assertIsNotNone(saved)
            self.assertEqual(saved["name"], "Produk Import Test")

            # Cleanup
            self.prod_repo.delete(saved["product_id"])


if __name__ == "__main__":
    unittest.main()
