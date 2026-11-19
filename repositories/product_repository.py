from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import get_connection


class ProductRepository:
    """Repository untuk operasi tabel products di database PostgreSQL."""

    def __init__(self, connection=None):
        self._connection = connection

    def _get_conn(self):
        return self._connection if self._connection else get_connection()

    def get_all(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT p.*, s.name as supplier_name, s.supplier_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                    ORDER BY p.product_id ASC
                    """
                )
                return cur.fetchall()

    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT p.*, s.name as supplier_name, s.supplier_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                    WHERE p.product_id = %s
                    """,
                    (product_id,),
                )
                return cur.fetchone()

    def get_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT p.*, s.name as supplier_name, s.supplier_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                    WHERE p.sku = %s
                    """,
                    (sku,),
                )
                return cur.fetchone()

    def create(
        self,
        sku: str,
        name: str,
        category: Optional[str] = None,
        supplier_id: Optional[int] = None,
        unit: str = "pcs",
        stock_quantity: float = 0,
        unit_cost: float = 0,
        selling_price: float = 0,
        minimum_stock: float = 0,
    ) -> Dict[str, Any]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO products (
                        sku, name, category, supplier_id, unit,
                        stock_quantity, unit_cost, selling_price, minimum_stock
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        sku,
                        name,
                        category,
                        supplier_id,
                        unit,
                        Decimal(str(stock_quantity)),
                        Decimal(str(unit_cost)),
                        Decimal(str(selling_price)),
                        Decimal(str(minimum_stock)),
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def update(
        self,
        product_id: int,
        name: str,
        category: Optional[str] = None,
        supplier_id: Optional[int] = None,
        unit: str = "pcs",
        unit_cost: float = 0,
        selling_price: float = 0,
        minimum_stock: float = 0,
    ) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE products
                    SET name = %s,
                        category = %s,
                        supplier_id = %s,
                        unit = %s,
                        unit_cost = %s,
                        selling_price = %s,
                        minimum_stock = %s
                    WHERE product_id = %s
                    RETURNING *
                    """,
                    (
                        name,
                        category,
                        supplier_id,
                        unit,
                        Decimal(str(unit_cost)),
                        Decimal(str(selling_price)),
                        Decimal(str(minimum_stock)),
                        product_id,
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def update_stock(self, product_id: int, quantity_change: float) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity + %s
                    WHERE product_id = %s
                    RETURNING *
                    """,
                    (Decimal(str(quantity_change)), product_id),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def delete(self, product_id: int) -> bool:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    def get_low_stock(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT p.*, s.name as supplier_name, s.supplier_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                    WHERE p.stock_quantity <= p.minimum_stock
                    ORDER BY p.stock_quantity ASC
                    """
                )
                return cur.fetchall()
