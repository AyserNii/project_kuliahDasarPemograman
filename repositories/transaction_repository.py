from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import get_connection


class TransactionRepository:
    """Repository untuk operasi tabel transactions di database PostgreSQL."""

    def __init__(self, connection=None):
        self._connection = connection

    def _get_conn(self):
        return self._connection if self._connection else get_connection()

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT t.*, p.sku, p.name as product_name, s.name as supplier_name
                    FROM transactions t
                    JOIN products p ON t.product_id = p.product_id
                    LEFT JOIN suppliers s ON t.supplier_id = s.supplier_id
                    ORDER BY t.transaction_date DESC
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
                    SELECT t.*, p.sku, p.name as product_name, s.name as supplier_name
                    FROM transactions t
                    JOIN products p ON t.product_id = p.product_id
                    LEFT JOIN suppliers s ON t.supplier_id = s.supplier_id
                    WHERE t.product_id = %s
                    ORDER BY t.transaction_date DESC
                    LIMIT %s
                    """,
                    (product_id, limit),
                )
                return cur.fetchall()

    def get_by_code(self, transaction_code: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT t.*, p.sku, p.name as product_name, s.name as supplier_name
                    FROM transactions t
                    JOIN products p ON t.product_id = p.product_id
                    LEFT JOIN suppliers s ON t.supplier_id = s.supplier_id
                    WHERE t.transaction_code = %s
                    """,
                    (transaction_code,),
                )
                return cur.fetchone()

    def create(
        self,
        transaction_code: str,
        product_id: int,
        transaction_type: str,
        quantity: float,
        unit_cost: float = 0,
        supplier_id: Optional[int] = None,
        notes: Optional[str] = None,
        transaction_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Mencatat transaksi dan langsung memperbarui stok produk dalam 1 database transaction.
        """
        transaction_type = transaction_type.upper()
        if transaction_type not in ("IN", "OUT"):
            raise ValueError("transaction_type harus 'IN' atau 'OUT'")

        qty_decimal = Decimal(str(quantity))
        if qty_decimal <= 0:
            raise ValueError("Kuantitas harus lebih besar dari 0")

        cost_decimal = Decimal(str(unit_cost))
        txn_date = transaction_date or datetime.now(timezone.utc)

        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Cek ketersediaan stok jika tipe OUT
                cur.execute(
                    "SELECT stock_quantity FROM products WHERE product_id = %s FOR UPDATE",
                    (product_id,),
                )
                prod = cur.fetchone()
                if not prod:
                    raise ValueError(f"Produk dengan ID {product_id} tidak ditemukan")

                current_stock = prod["stock_quantity"]
                if transaction_type == "OUT" and current_stock < qty_decimal:
                    raise ValueError(
                        f"Stok tidak mencukupi. Stok saat ini: {current_stock}, diminta: {qty_decimal}"
                    )

                # Simpan transaksi
                cur.execute(
                    """
                    INSERT INTO transactions (
                        transaction_code, product_id, supplier_id,
                        transaction_type, quantity, unit_cost, transaction_date, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        transaction_code,
                        product_id,
                        supplier_id,
                        transaction_type,
                        qty_decimal,
                        cost_decimal,
                        txn_date,
                        notes,
                    ),
                )
                txn = cur.fetchone()

                # Perbarui stok produk
                stock_diff = qty_decimal if transaction_type == "IN" else -qty_decimal
                cur.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity + %s
                    WHERE product_id = %s
                    """,
                    (stock_diff, product_id),
                )

                conn.commit()
                return txn
