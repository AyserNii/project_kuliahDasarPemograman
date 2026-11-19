from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from math import sqrt
from pathlib import Path

from database.connection import get_connection


SUPPLIERS = (
    ("SUP-001", "Sumber Pangan Nusantara", "Tim Penjualan", "021-555-0101", "Jakarta"),
)

PRODUCTS = (
    ("BRG-001", "Kopi Arabika 250 g", "Minuman", "SUP-001", "pcs", "93", "45000", "60000", "20"),
    ("BRG-002", "Teh Melati 100 g", "Minuman", "SUP-001", "pcs", "75", "18000", "25000", "15"),
)

TRANSACTIONS = (
    ("SEED-IN-001", "BRG-001", "SUP-001", "IN", "100", "45000", 30, "Stok awal"),
    ("SEED-IN-002", "BRG-002", "SUP-001", "IN", "80", "18000", 30, "Stok awal"),
    ("SEED-SALE-001", "BRG-001", None, "OUT", "7", "45000", 3, "Penjualan contoh"),
    ("SEED-SALE-002", "BRG-002", None, "OUT", "5", "18000", 2, "Penjualan contoh"),
)

SALES = (
    ("SEED-SALE-001", "BRG-001", "7", "60000", 3),
    ("SEED-SALE-002", "BRG-002", "5", "25000", 2),
)

ANALYSIS_INPUTS = (
    ("BRG-001", "2400", "50000", "12000", "8", "2", "5", "1.650"),
    ("BRG-002", "1800", "75000", "18000", "6", "1.5", "7", "1.650"),
)


def _decimal(value):
    return Decimal(str(value))


def _analysis_results(
    annual_demand,
    ordering_cost,
    holding_cost,
    average_daily_demand,
    daily_demand_stddev,
    lead_time_days,
    z_score,
):
    eoq = sqrt(
        (2 * float(annual_demand) * float(ordering_cost)) / float(holding_cost)
    )
    safety_stock = (
        float(z_score)
        * float(daily_demand_stddev)
        * sqrt(float(lead_time_days))
    )
    reorder_point = (
        float(average_daily_demand) * float(lead_time_days) + safety_stock
    )
    return (
        _decimal(f"{eoq:.2f}"),
        _decimal(f"{safety_stock:.2f}"),
        _decimal(f"{reorder_point:.2f}"),
    )


def seed_database():
    schema_sql = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    supplier_ids = {}
    product_ids = {}

    with get_connection() as connection:
        connection.execute(schema_sql)

        for code, name, contact, phone, address in SUPPLIERS:
            row = connection.execute(
                """
                INSERT INTO suppliers (supplier_code, name, contact_name, phone, address)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (supplier_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    contact_name = EXCLUDED.contact_name,
                    phone = EXCLUDED.phone,
                    address = EXCLUDED.address
                RETURNING supplier_id
                """,
                (code, name, contact, phone, address),
            ).fetchone()
            supplier_ids[code] = row[0]

        for (
            sku,
            name,
            category,
            supplier_code,
            unit,
            stock,
            unit_cost,
            selling_price,
            minimum_stock,
        ) in PRODUCTS:
            row = connection.execute(
                """
                INSERT INTO products (
                    sku, name, category, supplier_id, unit, stock_quantity,
                    unit_cost, selling_price, minimum_stock
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    supplier_id = EXCLUDED.supplier_id,
                    unit = EXCLUDED.unit,
                    stock_quantity = EXCLUDED.stock_quantity,
                    unit_cost = EXCLUDED.unit_cost,
                    selling_price = EXCLUDED.selling_price,
                    minimum_stock = EXCLUDED.minimum_stock
                RETURNING product_id
                """,
                (
                    sku,
                    name,
                    category,
                    supplier_ids[supplier_code],
                    unit,
                    _decimal(stock),
                    _decimal(unit_cost),
                    _decimal(selling_price),
                    _decimal(minimum_stock),
                ),
            ).fetchone()
            product_ids[sku] = row[0]

        for code, sku, supplier_code, kind, quantity, unit_cost, days_ago, notes in TRANSACTIONS:
            connection.execute(
                """
                INSERT INTO transactions (
                    transaction_code, product_id, supplier_id, transaction_type,
                    quantity, unit_cost, transaction_date, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_code) DO UPDATE SET
                    product_id = EXCLUDED.product_id,
                    supplier_id = EXCLUDED.supplier_id,
                    transaction_type = EXCLUDED.transaction_type,
                    quantity = EXCLUDED.quantity,
                    unit_cost = EXCLUDED.unit_cost,
                    notes = EXCLUDED.notes
                """,
                (
                    code,
                    product_ids[sku],
                    supplier_ids.get(supplier_code),
                    kind,
                    _decimal(quantity),
                    _decimal(unit_cost),
                    datetime.now(timezone.utc) - timedelta(days=days_ago),
                    notes,
                ),
            )

        for code, sku, quantity, unit_price, days_ago in SALES:
            transaction_id = connection.execute(
                "SELECT transaction_id FROM transactions WHERE transaction_code = %s",
                (code,),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO sales_history (
                    transaction_id, product_id, quantity_sold, unit_price, sale_date
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO UPDATE SET
                    product_id = EXCLUDED.product_id,
                    quantity_sold = EXCLUDED.quantity_sold,
                    unit_price = EXCLUDED.unit_price
                """,
                (
                    transaction_id,
                    product_ids[sku],
                    _decimal(quantity),
                    _decimal(unit_price),
                    datetime.now(timezone.utc) - timedelta(days=days_ago),
                ),
            )

        for sku, *raw_inputs in ANALYSIS_INPUTS:
            inputs = tuple(_decimal(value) for value in raw_inputs)
            eoq, safety_stock, reorder_point = _analysis_results(*inputs)
            connection.execute(
                """
                INSERT INTO inventory_analysis (
                    product_id, analysis_date, annual_demand, ordering_cost,
                    holding_cost_per_unit_year, average_daily_demand,
                    daily_demand_stddev, lead_time_days, z_score, eoq,
                    safety_stock, reorder_point
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
                """,
                (
                    product_ids[sku],
                    date.today(),
                    *inputs,
                    eoq,
                    safety_stock,
                    reorder_point,
                ),
            )


if __name__ == "__main__":
    seed_database()
    print("Skema database dan data contoh berhasil disiapkan.")