from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from config.settings import EXPORT_BACKUPS_DIR, EXPORT_REPORTS_DIR
from repositories.analysis_repository import AnalysisRepository
from repositories.product_repository import ProductRepository
from repositories.sales_repository import SalesRepository
from repositories.transaction_repository import TransactionRepository


class ExportService:
    """
    Service untuk mengekspor data PostgreSQL menjadi format CSV
    menggunakan library Pandas DataFrame (to_csv).
    """

    def __init__(
        self,
        product_repo: ProductRepository = None,
        transaction_repo: TransactionRepository = None,
        sales_repo: SalesRepository = None,
        analysis_repo: AnalysisRepository = None,
    ):
        self.product_repo = product_repo or ProductRepository()
        self.transaction_repo = transaction_repo or TransactionRepository()
        self.sales_repo = sales_repo or SalesRepository()
        self.analysis_repo = analysis_repo or AnalysisRepository()

    def export_products_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export seluruh data produk ke file CSV via Pandas DataFrame."""
        products = self.product_repo.get_all()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = output_path or (EXPORT_BACKUPS_DIR / f"products_backup_{timestamp}.csv")

        df = pd.DataFrame(products)
        df.to_csv(target_file, index=False)
        return target_file

    def export_transactions_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export riwayat transaksi masuk & keluar ke file CSV via Pandas DataFrame."""
        transactions = self.transaction_repo.get_all(limit=1000)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = output_path or (EXPORT_BACKUPS_DIR / f"transactions_backup_{timestamp}.csv")

        df = pd.DataFrame(transactions)
        df.to_csv(target_file, index=False)
        return target_file

    def export_sales_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export riwayat penjualan ke file CSV via Pandas DataFrame."""
        sales = self.sales_repo.get_all(limit=1000)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = output_path or (EXPORT_REPORTS_DIR / f"sales_report_{timestamp}.csv")

        df = pd.DataFrame(sales)
        df.to_csv(target_file, index=False)
        return target_file

    def export_inventory_analysis_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export hasil perhitungan optimasi persediaan (EOQ, ROP, SS) ke file CSV via Pandas."""
        analyses = self.analysis_repo.get_all_latest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = output_path or (EXPORT_REPORTS_DIR / f"inventory_analysis_{timestamp}.csv")

        df = pd.DataFrame(analyses)
        df.to_csv(target_file, index=False)
        return target_file
