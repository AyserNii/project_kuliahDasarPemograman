from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import get_connection


class AnalysisRepository:
    """Repository untuk operasi tabel inventory_analysis di database PostgreSQL."""

    def __init__(self, connection=None):
        self._connection = connection

    def _get_conn(self):
        return self._connection if self._connection else get_connection()

    def save(
        self,
        product_id: int,
        annual_demand: float,
        ordering_cost: float,
        holding_cost_per_unit_year: float,
        average_daily_demand: float,
        daily_demand_stddev: float,
        lead_time_days: float,
        z_score: float,
        eoq: float,
        safety_stock: float,
        reorder_point: float,
        analysis_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        target_date = analysis_date or date.today()

        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO inventory_analysis (
                        product_id, analysis_date, annual_demand, ordering_cost,
                        holding_cost_per_unit_year, average_daily_demand,
                        daily_demand_stddev, lead_time_days, z_score,
                        eoq, safety_stock, reorder_point
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id, analysis_date) DO UPDATE SET
                        annual_demand = EXCLUDED.annual_demand,
                        ordering_cost = EXCLUDED.ordering_cost,
                        holding_cost_per_unit_year = EXCLUDED.holding_cost_per_unit_year,
                        average_daily_demand = EXCLUDED.average_daily_demand,
                        daily_demand_stddev = EXCLUDED.daily_demand_stddev,
                        lead_time_days = EXCLUDED.lead_time_days,
                        z_score = EXCLUDED.z_score,
                        eoq = EXCLUDED.eoq,
                        safety_stock = EXCLUDED.safety_stock,
                        reorder_point = EXCLUDED.reorder_point
                    RETURNING *
                    """,
                    (
                        product_id,
                        target_date,
                        Decimal(str(round(annual_demand, 2))),
                        Decimal(str(round(ordering_cost, 2))),
                        Decimal(str(round(holding_cost_per_unit_year, 2))),
                        Decimal(str(round(average_daily_demand, 2))),
                        Decimal(str(round(daily_demand_stddev, 2))),
                        Decimal(str(round(lead_time_days, 2))),
                        Decimal(str(round(z_score, 3))),
                        Decimal(str(round(eoq, 2))),
                        Decimal(str(round(safety_stock, 2))),
                        Decimal(str(round(reorder_point, 2))),
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def get_latest_by_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT a.*, p.sku, p.name as product_name, p.stock_quantity, p.unit
                    FROM inventory_analysis a
                    JOIN products p ON a.product_id = p.product_id
                    WHERE a.product_id = %s
                    ORDER BY a.analysis_date DESC
                    LIMIT 1
                    """,
                    (product_id,),
                )
                return cur.fetchone()

    def get_all_latest(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT DISTINCT ON (a.product_id)
                        a.*, p.sku, p.name as product_name, p.stock_quantity, p.unit, p.unit_cost
                    FROM inventory_analysis a
                    JOIN products p ON a.product_id = p.product_id
                    ORDER BY a.product_id, a.analysis_date DESC
                    """
                )
                return cur.fetchall()

    def get_history_by_product(self, product_id: int, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT a.*, p.sku, p.name as product_name
                    FROM inventory_analysis a
                    JOIN products p ON a.product_id = p.product_id
                    WHERE a.product_id = %s
                    ORDER BY a.analysis_date DESC
                    LIMIT %s
                    """,
                    (product_id, limit),
                )
                return cur.fetchall()
