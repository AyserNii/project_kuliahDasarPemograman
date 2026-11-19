from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from psycopg.rows import dict_row

from database.connection import get_connection


class SalesRepository:
    """Repository untuk operasi tabel sales_history di database PostgreSQL."""

    def __init__(self, connection=None):
        self._connection = connection

    def _get_conn(self):
        return self._connection if self._connection else get_connection()

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT s.*, p.sku, p.name as product_name, t.transaction_code
                    FROM sales_history s
                    JOIN products p ON s.product_id = p.product_id
                    JOIN transactions t ON s.transaction_id = t.transaction_id
                    ORDER BY s.sale_date DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return cur.fetchall()

    def get_by_product(self, product_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT s.*, p.sku, p.name as product_name, t.transaction_code
                    FROM sales_history s
                    JOIN products p ON s.product_id = p.product_id
                    JOIN transactions t ON s.transaction_id = t.transaction_id
                    WHERE s.product_id = %s
                    ORDER BY s.sale_date DESC
                    LIMIT %s
                    """,
                    (product_id, limit),
                )
                return cur.fetchall()

    def record_sale(
        self,
        product_id: int,
        quantity_sold: float,
        unit_price: float,
        transaction_code: Optional[str] = None,
        sale_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mencatat penjualan: membuat transaksi OUT, memperbarui stok produk,
        dan menyimpan baris ke sales_history.
        """
        qty = Decimal(str(quantity_sold))
        if qty <= 0:
            raise ValueError("Kuantitas penjualan harus lebih besar dari 0")

        price = Decimal(str(unit_price))
        if price < 0:
            raise ValueError("Harga satuan tidak boleh negatif")

        dt = sale_date or datetime.now(timezone.utc)
        code = transaction_code or f"SALE-{uuid.uuid4().hex[:8].upper()}"

        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Cek stok saat ini
                cur.execute(
                    "SELECT stock_quantity, unit_cost FROM products WHERE product_id = %s FOR UPDATE",
                    (product_id,),
                )
                prod = cur.fetchone()
                if not prod:
                    raise ValueError(f"Produk dengan ID {product_id} tidak ditemukan")

                if prod["stock_quantity"] < qty:
                    raise ValueError(
                        f"Stok tidak mencukupi untuk penjualan. Stok: {prod['stock_quantity']}, diminta: {qty}"
                    )

                unit_cost = prod["unit_cost"]

                # 1. Masukkan ke transactions (OUT)
                cur.execute(
                    """
                    INSERT INTO transactions (
                        transaction_code, product_id, supplier_id,
                        transaction_type, quantity, unit_cost, transaction_date, notes
                    )
                    VALUES (%s, %s, NULL, 'OUT', %s, %s, %s, %s)
                    RETURNING transaction_id
                    """,
                    (code, product_id, qty, unit_cost, dt, notes or "Penjualan Barang"),
                )
                txn_id = cur.fetchone()["transaction_id"]

                # 2. Kurangi stok produk
                cur.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity - %s
                    WHERE product_id = %s
                    """,
                    (qty, product_id),
                )

                # 3. Masukkan ke sales_history
                cur.execute(
                    """
                    INSERT INTO sales_history (
                        transaction_id, product_id, quantity_sold, unit_price, sale_date, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (txn_id, product_id, qty, price, dt, notes),
                )
                sale_record = cur.fetchone()

                conn.commit()
                return sale_record

    def get_daily_sales(self, product_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """Mengambil rekap penjualan harian produk untuk analisis peramalan."""
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT DATE(sale_date) as sale_day,
                           SUM(quantity_sold) as total_quantity,
                           SUM(quantity_sold * unit_price) as total_revenue,
                           COUNT(*) as transaction_count
                    FROM sales_history
                    WHERE product_id = %s
                      AND sale_date >= CURRENT_DATE - (%s || ' days')::INTERVAL
                    GROUP BY DATE(sale_date)
                    ORDER BY sale_day ASC
                    """,
                    (product_id, days),
                )
                return cur.fetchall()
