from datetime import date
from typing import Any, Dict, List, Optional

from config.settings import (
    DEFAULT_HOLDING_COST_RATE,
    DEFAULT_LEAD_TIME_DAYS,
    DEFAULT_ORDERING_COST,
    DEFAULT_SERVICE_LEVEL_Z,
)
from modules.analysis import determine_stock_status, generate_recommendation
from modules.forecasting import calculate_demand_statistics
from modules.inventory import (
    calculate_eoq,
    calculate_inventory_costs,
    calculate_reorder_point,
    calculate_safety_stock,
)
from repositories.analysis_repository import AnalysisRepository
from repositories.product_repository import ProductRepository
from repositories.sales_repository import SalesRepository


class InventoryService:
    """Service untuk mengatur alur proses pengelolaan dan optimasi inventory."""

    def __init__(
        self,
        product_repo: ProductRepository = None,
        sales_repo: SalesRepository = None,
        analysis_repo: AnalysisRepository = None,
    ):
        self.product_repo = product_repo or ProductRepository()
        self.sales_repo = sales_repo or SalesRepository()
        self.analysis_repo = analysis_repo or AnalysisRepository()

    def analyze_product(
        self,
        product_id: int,
        ordering_cost: Optional[float] = None,
        holding_cost_rate: Optional[float] = None,
        lead_time_days: Optional[float] = None,
        z_score: Optional[float] = None,
        manual_annual_demand: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Menjalankan analisis persediaan untuk satu produk:
        1. Mengambil data produk & harga modal
        2. Menghitung rata-rata permintaan harian & deviasi dari riwayat penjualan
        3. Menghitung EOQ, Safety Stock, Reorder Point
        4. Menyimpan hasil perhitungan ke tabel inventory_analysis di database
        """
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Produk dengan ID {product_id} tidak ditemukan.")

        s_cost = float(ordering_cost if ordering_cost is not None else DEFAULT_ORDERING_COST)
        h_rate = float(holding_cost_rate if holding_cost_rate is not None else DEFAULT_HOLDING_COST_RATE)
        l_days = float(lead_time_days if lead_time_days is not None else DEFAULT_LEAD_TIME_DAYS)
        z = float(z_score if z_score is not None else DEFAULT_SERVICE_LEVEL_Z)

        # Hitung holding cost per unit per tahun (berdasarkan unit_cost * h_rate)
        unit_cost = float(product.get("unit_cost", 0))
        holding_cost_per_unit = unit_cost * h_rate
        if holding_cost_per_unit <= 0:
            holding_cost_per_unit = 1000.0  # Nilai minimal wajar jika unit_cost 0

        # Ambil statistik penjualan
        daily_sales = self.sales_repo.get_daily_sales(product_id, days=180)
        quantities = [float(row["total_quantity"]) for row in daily_sales]

        stats = calculate_demand_statistics(quantities)

        if manual_annual_demand is not None and manual_annual_demand > 0:
            annual_demand = float(manual_annual_demand)
            avg_daily_demand = annual_demand / 365.0
            std_dev = stats["daily_demand_stddev"]
        elif stats["annual_demand"] > 0:
            annual_demand = stats["annual_demand"]
            avg_daily_demand = stats["average_daily_demand"]
            std_dev = stats["daily_demand_stddev"]
        else:
            # Fallback jika belum ada data riwayat penjualan yang cukup
            # Gunakan perkiraan dari minimum_stock atau stok saat ini
            min_stock = float(product.get("minimum_stock", 10))
            annual_demand = max(min_stock * 12, 120.0)
            avg_daily_demand = annual_demand / 365.0
            std_dev = max(avg_daily_demand * 0.25, 1.0)

        # Hitung metode persediaan
        eoq = calculate_eoq(annual_demand, s_cost, holding_cost_per_unit)
        safety_stock = calculate_safety_stock(std_dev, l_days, z)
        reorder_point = calculate_reorder_point(avg_daily_demand, l_days, safety_stock)

        # Simpan ke database
        saved_row = self.analysis_repo.save(
            product_id=product_id,
            annual_demand=annual_demand,
            ordering_cost=s_cost,
            holding_cost_per_unit_year=holding_cost_per_unit,
            average_daily_demand=avg_daily_demand,
            daily_demand_stddev=std_dev,
            lead_time_days=l_days,
            z_score=z,
            eoq=eoq,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            analysis_date=date.today(),
        )

        # Rekomendasi
        current_stock = float(product.get("stock_quantity", 0))
        rec = generate_recommendation(
            product_name=product["name"],
            current_stock=current_stock,
            reorder_point=reorder_point,
            safety_stock=safety_stock,
            eoq=eoq,
        )

        costs = calculate_inventory_costs(annual_demand, eoq, s_cost, holding_cost_per_unit)

        return {
            "product": product,
            "analysis": saved_row,
            "recommendation": rec,
            "costs": costs,
        }

    def analyze_all_products(self) -> List[Dict[str, Any]]:
        """Menjalankan analisis untuk seluruh produk yang terdaftar."""
        products = self.product_repo.get_all()
        results = []
        for p in products:
            try:
                res = self.analyze_product(p["product_id"])
                results.append(res)
            except Exception as e:
                results.append({"product": p, "error": str(e)})
        return results

    def get_inventory_dashboard_data(self) -> Dict[str, Any]:
        """Mengumpulkan data metrik status persediaan seluruh produk."""
        products = self.product_repo.get_all()
        analyses = {a["product_id"]: a for a in self.analysis_repo.get_all_latest()}

        dashboard_rows = []
        total_asset_value = 0.0

        for p in products:
            pid = p["product_id"]
            curr_stock = float(p.get("stock_quantity", 0))
            cost = float(p.get("unit_cost", 0))
            total_asset_value += curr_stock * cost

            analysis = analyses.get(pid)
            if analysis:
                rop = float(analysis["reorder_point"])
                ss = float(analysis["safety_stock"])
                eoq = float(analysis["eoq"])
            else:
                rop = float(p.get("minimum_stock", 0))
                ss = 0.0
                eoq = 0.0

            status = determine_stock_status(curr_stock, rop, ss)
            dashboard_rows.append({
                "product_id": pid,
                "sku": p["sku"],
                "name": p["name"],
                "category": p.get("category") or "-",
                "unit": p.get("unit", "pcs"),
                "stock_quantity": curr_stock,
                "reorder_point": rop,
                "safety_stock": ss,
                "eoq": eoq,
                "status": status,
            })

        return {
            "total_products": len(products),
            "total_asset_value": total_asset_value,
            "items": dashboard_rows,
        }
