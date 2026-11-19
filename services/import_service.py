from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd

from config.settings import IMPORTS_DIR
from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository


class ImportService:
    """
    Service untuk membaca file CSV menggunakan library Pandas (pd.read_csv)
    dan menyimpannya ke database PostgreSQL.
    """

    def __init__(
        self,
        product_repo: ProductRepository = None,
        supplier_repo: SupplierRepository = None,
    ):
        self.product_repo = product_repo or ProductRepository()
        self.supplier_repo = supplier_repo or SupplierRepository()

    def import_suppliers_from_csv(self, file_path: Path) -> Tuple[int, int, List[str]]:
        """
        Import data supplier dari file CSV menggunakan Pandas DataFrame.
        Format kolom: supplier_code, name, contact_name, phone, address
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        # Membaca data CSV ke dalam Pandas DataFrame
        df = pd.read_csv(file_path, dtype=str).fillna("")

        success_count = 0
        fail_count = 0
        errors = []

        for index, row in df.iterrows():
            row_num = index + 2  # Nomor baris pada file CSV (termasuk header)
            try:
                code = str(row.get("supplier_code", "")).strip().upper()
                name = str(row.get("name", "")).strip()

                if not code or not name:
                    raise ValueError("supplier_code dan name wajib diisi")

                existing = self.supplier_repo.get_by_code(code)
                if existing:
                    errors.append(f"Baris {row_num}: Supplier dengan kode {code} sudah terdaftar.")
                    fail_count += 1
                    continue

                contact = str(row.get("contact_name", "")).strip() or None
                phone = str(row.get("phone", "")).strip() or None
                address = str(row.get("address", "")).strip() or None

                self.supplier_repo.create(
                    supplier_code=code,
                    name=name,
                    contact_name=contact,
                    phone=phone,
                    address=address,
                )
                success_count += 1
            except Exception as err:
                fail_count += 1
                errors.append(f"Baris {row_num}: {err}")

        return success_count, fail_count, errors

    def import_products_from_csv(self, file_path: Path) -> Tuple[int, int, List[str]]:
        """
        Import data produk dari file CSV menggunakan Pandas DataFrame.
        Format kolom: sku, name, category, supplier_code, unit, stock_quantity, unit_cost, selling_price, minimum_stock
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        # Membaca data CSV ke dalam Pandas DataFrame
        df = pd.read_csv(file_path, dtype=str).fillna("")

        success_count = 0
        fail_count = 0
        errors = []

        for index, row in df.iterrows():
            row_num = index + 2
            try:
                sku = str(row.get("sku", "")).strip().upper()
                name = str(row.get("name", "")).strip()

                if not sku or not name:
                    raise ValueError("sku dan name wajib diisi")

                existing = self.product_repo.get_by_sku(sku)
                if existing:
                    errors.append(f"Baris {row_num}: Produk dengan SKU {sku} sudah terdaftar.")
                    fail_count += 1
                    continue

                # Pencocokan supplier
                supplier_id = None
                sup_code = str(row.get("supplier_code", "")).strip().upper()
                if sup_code:
                    sup = self.supplier_repo.get_by_code(sup_code)
                    if sup:
                        supplier_id = sup["supplier_id"]

                unit = str(row.get("unit", "")).strip() or "pcs"
                stock = float(row.get("stock_quantity", 0) or 0)
                cost = float(row.get("unit_cost", 0) or 0)
                price = float(row.get("selling_price", 0) or 0)
                min_stock = float(row.get("minimum_stock", 0) or 0)

                self.product_repo.create(
                    sku=sku,
                    name=name,
                    category=str(row.get("category", "")).strip() or None,
                    supplier_id=supplier_id,
                    unit=unit,
                    stock_quantity=stock,
                    unit_cost=cost,
                    selling_price=price,
                    minimum_stock=min_stock,
                )
                success_count += 1
            except Exception as err:
                fail_count += 1
                errors.append(f"Baris {row_num}: {err}")

        return success_count, fail_count, errors

    def generate_sample_templates(self):
        """Membuat template CSV di storage/imports/ menggunakan Pandas."""
        prod_data = {
            "sku": ["BRG-003", "BRG-004"],
            "name": ["Susu Bubuk 500g", "Sirup Karamel 750ml"],
            "category": ["Bahan Minuman", "Bahan Minuman"],
            "supplier_code": ["SUP-001", "SUP-001"],
            "unit": ["pcs", "botol"],
            "stock_quantity": [50, 30],
            "unit_cost": [25000, 45000],
            "selling_price": [32000, 58000],
            "minimum_stock": [10, 8],
        }
        df_prod = pd.DataFrame(prod_data)
        df_prod.to_csv(IMPORTS_DIR / "template_products.csv", index=False)

        sup_data = {
            "supplier_code": ["SUP-002"],
            "name": ["Distributor Bahan Baku Sejahtera"],
            "contact_name": ["Budi Santoso"],
            "phone": ["081234567890"],
            "address": ["Bandung"],
        }
        df_sup = pd.DataFrame(sup_data)
        df_sup.to_csv(IMPORTS_DIR / "template_suppliers.csv", index=False)
