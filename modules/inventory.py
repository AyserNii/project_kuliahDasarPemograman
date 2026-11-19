from decimal import Decimal
import math
from typing import Dict


def calculate_eoq(
    annual_demand: float,
    ordering_cost: float,
    holding_cost_per_unit_year: float,
) -> float:
    """
    Menghitung Economic Order Quantity (EOQ).
    Rumus: sqrt((2 * D * S) / H)
    - D: Annual Demand (Permintaan tahunan)
    - S: Ordering Cost (Biaya pemesanan per pesanan)
    - H: Holding Cost (Biaya penyimpanan per unit per tahun)
    """
    if annual_demand <= 0:
        raise ValueError("Permintaan tahunan (annual demand) harus > 0")
    if ordering_cost < 0:
        raise ValueError("Biaya pemesanan (ordering cost) tidak boleh negatif")
    if holding_cost_per_unit_year <= 0:
        raise ValueError("Biaya penyimpanan per unit (holding cost) harus > 0")

    eoq_val = math.sqrt((2 * float(annual_demand) * float(ordering_cost)) / float(holding_cost_per_unit_year))
    return round(eoq_val, 2)


def calculate_safety_stock(
    daily_demand_stddev: float,
    lead_time_days: float,
    z_score: float = 1.65,
) -> float:
    """
    Menghitung Safety Stock (Persediaan Pengaman).
    Rumus: Z * stddev_d * sqrt(L)
    - Z: Service level factor (misal 1.65 untuk tingkat pelayanan ~95%)
    - stddev_d: Standar deviasi permintaan harian
    - L: Waktu tunggu (lead time dalam hari)
    """
    if daily_demand_stddev < 0:
        raise ValueError("Standar deviasi permintaan tidak boleh negatif")
    if lead_time_days < 0:
        raise ValueError("Lead time tidak boleh negatif")
    if z_score < 0:
        raise ValueError("Nilai Z-score tidak boleh negatif")

    ss_val = float(z_score) * float(daily_demand_stddev) * math.sqrt(float(lead_time_days))
    return round(ss_val, 2)


def calculate_reorder_point(
    average_daily_demand: float,
    lead_time_days: float,
    safety_stock: float,
) -> float:
    """
    Menghitung Reorder Point (Titik Pemesanan Kembali).
    Rumus: (d * L) + SS
    - d: Rata-rata permintaan harian
    - L: Lead time dalam hari
    - SS: Safety Stock
    """
    if average_daily_demand < 0:
        raise ValueError("Rata-rata permintaan harian tidak boleh negatif")
    if lead_time_days < 0:
        raise ValueError("Lead time tidak boleh negatif")
    if safety_stock < 0:
        raise ValueError("Safety stock tidak boleh negatif")

    rop_val = (float(average_daily_demand) * float(lead_time_days)) + float(safety_stock)
    return round(rop_val, 2)


def calculate_inventory_costs(
    annual_demand: float,
    order_quantity: float,
    ordering_cost: float,
    holding_cost_per_unit_year: float,
) -> Dict[str, float]:
    """
    Menghitung total biaya persediaan berdasarkan kuantitas pesanan.
    - Annual Ordering Cost = (D / Q) * S
    - Annual Holding Cost = (Q / 2) * H
    - Total Variable Cost = Ordering Cost + Holding Cost
    """
    d = float(annual_demand)
    q = float(order_quantity)
    s = float(ordering_cost)
    h = float(holding_cost_per_unit_year)

    if q <= 0:
        raise ValueError("Kuantitas pemesanan (Q) harus > 0")

    annual_ordering_cost = (d / q) * s
    annual_holding_cost = (q / 2) * h
    total_cost = annual_ordering_cost + annual_holding_cost
    number_of_orders = d / q
    order_cycle_days = (q / d) * 365 if d > 0 else 0

    return {
        "order_quantity": round(q, 2),
        "annual_ordering_cost": round(annual_ordering_cost, 2),
        "annual_holding_cost": round(annual_holding_cost, 2),
        "total_cost": round(total_cost, 2),
        "number_of_orders_per_year": round(number_of_orders, 2),
        "order_cycle_days": round(order_cycle_days, 1),
    }


def analyze_inventory_item(
    annual_demand: float,
    ordering_cost: float,
    holding_cost_per_unit_year: float,
    average_daily_demand: float,
    daily_demand_stddev: float,
    lead_time_days: float,
    z_score: float = 1.65,
) -> Dict[str, float]:
    """
    Melakukan perhitungan menyeluruh untuk satu item inventaris.
    """
    eoq = calculate_eoq(annual_demand, ordering_cost, holding_cost_per_unit_year)
    safety_stock = calculate_safety_stock(daily_demand_stddev, lead_time_days, z_score)
    reorder_point = calculate_reorder_point(average_daily_demand, lead_time_days, safety_stock)
    costs = calculate_inventory_costs(annual_demand, eoq, ordering_cost, holding_cost_per_unit_year)

    return {
        "eoq": eoq,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        **costs,
    }
