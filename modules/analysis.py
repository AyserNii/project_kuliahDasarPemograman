from typing import Any, Dict
from modules.inventory import calculate_inventory_costs


def determine_stock_status(current_stock: float, reorder_point: float, safety_stock: float = 0) -> str:
    """
    Menentukan status kesehatan stok produk:
    - HABIS: Stok 0 atau kurang
    - KRITIS: Stok di bawah atau sama dengan Safety Stock
    - PERLU REORDER: Stok di bawah atau sama dengan Reorder Point
    - AMAN: Stok berada di atas Reorder Point
    """
    curr = float(current_stock)
    rop = float(reorder_point)
    ss = float(safety_stock)

    if curr <= 0:
        return "HABIS"
    if ss > 0 and curr <= ss:
        return "KRITIS"
    if curr <= rop:
        return "PERLU REORDER"
    return "AMAN"


def compare_inventory_policies(
    annual_demand: float,
    current_order_qty: float,
    eoq_qty: float,
    ordering_cost: float,
    holding_cost_per_unit_year: float,
) -> Dict[str, Any]:
    """
    Membandingkan biaya kebijakan pemesanan konvensional (saat ini) dengan kebijakan EOQ.
    Menghitung potensi penghematan biaya operasional persediaan.
    """
    current_costs = calculate_inventory_costs(
        annual_demand, current_order_qty, ordering_cost, holding_cost_per_unit_year
    )
    eoq_costs = calculate_inventory_costs(
        annual_demand, eoq_qty, ordering_cost, holding_cost_per_unit_year
    )

    savings = current_costs["total_cost"] - eoq_costs["total_cost"]
    savings_pct = (savings / current_costs["total_cost"] * 100) if current_costs["total_cost"] > 0 else 0

    return {
        "current_policy": current_costs,
        "eoq_policy": eoq_costs,
        "annual_savings": round(max(0.0, savings), 2),
        "savings_percentage": round(max(0.0, savings_pct), 2),
    }


def generate_recommendation(
    product_name: str,
    current_stock: float,
    reorder_point: float,
    safety_stock: float,
    eoq: float,
) -> Dict[str, Any]:
    """
    Menghasilkan rekomendasi tindakan konkret untuk manajemen persediaan barang.
    """
    status = determine_stock_status(current_stock, reorder_point, safety_stock)

    if status in ("HABIS", "KRITIS", "PERLU REORDER"):
        action = f"Lakukan pemesanan ulang segera sebesar {eoq:.0f} unit (sesuai EOQ)."
        priority = "TINGGI" if status in ("HABIS", "KRITIS") else "SEDANG"
    else:
        action = "Stok masih mencukupi. Pertahankan tingkat persediaan saat ini."
        priority = "RENDAH"

    return {
        "product_name": product_name,
        "current_stock": round(float(current_stock), 2),
        "reorder_point": round(float(reorder_point), 2),
        "safety_stock": round(float(safety_stock), 2),
        "eoq": round(float(eoq), 2),
        "status": status,
        "priority": priority,
        "action": action,
    }
