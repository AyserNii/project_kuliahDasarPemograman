import unittest
import uuid
from database.connection import get_connection
from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository
from repositories.transaction_repository import TransactionRepository
from repositories.sales_repository import SalesRepository
from repositories.analysis_repository import AnalysisRepository


class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.prod_repo = ProductRepository()
        self.sup_repo = SupplierRepository()
        self.txn_repo = TransactionRepository()
        self.sales_repo = SalesRepository()
        self.analysis_repo = AnalysisRepository()

    def test_database_connection(self):
        with get_connection() as conn:
            self.assertIsNotNone(conn)

    def test_supplier_crud(self):
        unique_code = f"TEST-SUP-{uuid.uuid4().hex[:6].upper()}"
        sup = self.sup_repo.create(
            supplier_code=unique_code,
            name="Test Supplier PT",
            contact_name="Bambang",
            phone="081299998888",
            address="Surabaya",
        )
        self.assertEqual(sup["supplier_code"], unique_code)

        fetched = self.sup_repo.get_by_code(unique_code)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["name"], "Test Supplier PT")

        # Cleanup
        self.sup_repo.delete(sup["supplier_id"])

    def test_product_lifecycle(self):
        unique_sku = f"TEST-BRG-{uuid.uuid4().hex[:6].upper()}"
        prod = self.prod_repo.create(
            sku=unique_sku,
            name="Barang Percobaan",
            category="Uji Coba",
            unit="pcs",
            stock_quantity=50,
            unit_cost=10000,
            selling_price=15000,
            minimum_stock=10,
        )
        self.assertEqual(prod["sku"], unique_sku)
        self.assertEqual(float(prod["stock_quantity"]), 50.0)

        # Update stok
        updated = self.prod_repo.update_stock(prod["product_id"], 15)
        self.assertEqual(float(updated["stock_quantity"]), 65.0)

        # Cleanup
        self.prod_repo.delete(prod["product_id"])


if __name__ == "__main__":
    unittest.main()
