from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import get_connection


class SupplierRepository:
    """Repository untuk operasi tabel suppliers di database PostgreSQL."""

    def __init__(self, connection=None):
        self._connection = connection

    def _get_conn(self):
        return self._connection if self._connection else get_connection()

    def get_all(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT * FROM suppliers
                    ORDER BY supplier_id ASC
                    """
                )
                return cur.fetchall()

    def get_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM suppliers WHERE supplier_id = %s",
                    (supplier_id,),
                )
                return cur.fetchone()

    def get_by_code(self, supplier_code: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM suppliers WHERE supplier_code = %s",
                    (supplier_code,),
                )
                return cur.fetchone()

    def create(
        self,
        supplier_code: str,
        name: str,
        contact_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO suppliers (supplier_code, name, contact_name, phone, address)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (supplier_code, name, contact_name, phone, address),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def update(
        self,
        supplier_id: int,
        name: str,
        contact_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE suppliers
                    SET name = %s,
                        contact_name = %s,
                        phone = %s,
                        address = %s
                    WHERE supplier_id = %s
                    RETURNING *
                    """,
                    (name, contact_name, phone, address, supplier_id),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def delete(self, supplier_id: int) -> bool:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM suppliers WHERE supplier_id = %s",
                    (supplier_id,),
                )
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
