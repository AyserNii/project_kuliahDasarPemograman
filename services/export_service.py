from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from config.settings import DIREKTORI_CADANGAN_EKSPOR, DIREKTORI_LAPORAN_EKSPOR
from repositories.analysis_repository import RepositoriAnalisis
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan
from repositories.transaction_repository import RepositoriTransaksi


class LayananEkspor:
    """
    Service untuk mengekspor data PostgreSQL menjadi format CSV
    menggunakan library Pandas DataFrame (to_csv).
    """

    def __init__(
        self,
        repositori_produk: RepositoriProduk = None,
        repositori_transaksi: RepositoriTransaksi = None,
        repositori_penjualan: RepositoriPenjualan = None,
        repositori_analisis: RepositoriAnalisis = None,
    ):
        self.repositori_produk = repositori_produk or RepositoriProduk()
        self.repositori_transaksi = repositori_transaksi or RepositoriTransaksi()
        self.repositori_penjualan = repositori_penjualan or RepositoriPenjualan()
        self.repositori_analisis = repositori_analisis or RepositoriAnalisis()

    def ekspor_produk_ke_csv(self, jalur_keluaran: Optional[Path] = None) -> Path:
        """Export seluruh data produk ke file CSV via Pandas DataFrame."""
        daftar_produk = self.repositori_produk.ambil_semua()
        cap_waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
        berkas_tujuan = jalur_keluaran or (DIREKTORI_CADANGAN_EKSPOR / f"products_backup_{cap_waktu}.csv")

        kerangka_data = pd.DataFrame(daftar_produk)
        kerangka_data.to_csv(berkas_tujuan, index=False)
        return berkas_tujuan

    def ekspor_transaksi_ke_csv(self, jalur_keluaran: Optional[Path] = None) -> Path:
        """Export riwayat transaksi masuk & keluar ke file CSV via Pandas DataFrame."""
        daftar_transaksi = self.repositori_transaksi.ambil_semua(batas=1000)
        cap_waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
        berkas_tujuan = jalur_keluaran or (DIREKTORI_CADANGAN_EKSPOR / f"transactions_backup_{cap_waktu}.csv")

        kerangka_data = pd.DataFrame(daftar_transaksi)
        kerangka_data.to_csv(berkas_tujuan, index=False)
        return berkas_tujuan

    def ekspor_penjualan_ke_csv(self, jalur_keluaran: Optional[Path] = None) -> Path:
        """Export riwayat penjualan ke file CSV via Pandas DataFrame."""
        daftar_penjualan = self.repositori_penjualan.ambil_semua(batas=1000)
        cap_waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
        berkas_tujuan = jalur_keluaran or (DIREKTORI_LAPORAN_EKSPOR / f"sales_report_{cap_waktu}.csv")

        kerangka_data = pd.DataFrame(daftar_penjualan)
        kerangka_data.to_csv(berkas_tujuan, index=False)
        return berkas_tujuan

    def ekspor_analisis_persediaan_ke_csv(self, jalur_keluaran: Optional[Path] = None) -> Path:
        """Export hasil perhitungan optimasi persediaan (EOQ, ROP, SS) ke file CSV via Pandas."""
        daftar_analisis = self.repositori_analisis.ambil_semua_terbaru()
        cap_waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
        berkas_tujuan = jalur_keluaran or (DIREKTORI_LAPORAN_EKSPOR / f"inventory_analysis_{cap_waktu}.csv")

        kerangka_data = pd.DataFrame(daftar_analisis)
        kerangka_data.to_csv(berkas_tujuan, index=False)
        return berkas_tujuan
