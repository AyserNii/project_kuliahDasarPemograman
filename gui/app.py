import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Type
from gui.theme import (
    BG_CARD,
    BG_MAIN,
    BG_SIDEBAR,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
)
from gui.sidebar import Sidebar
from gui.header import Header
from gui.pages.dashboard import DashboardPage
from gui.pages.products import ProductsPage
from gui.pages.suppliers import SuppliersPage
from gui.pages.transactions import TransactionsPage
from gui.pages.sales import SalesPage
from gui.pages.inventory_analysis import InventoryAnalysisPage
from gui.pages.forecasting import ForecastingPage
from gui.pages.import_export import ImportExportPage
from gui.pages.reports import ReportsPage


PAGE_INFO = {
    "dashboard": {
        "title": "Dasbor Utama",
        "subtitle": "Pantau metrik persediaan, peringatan stok, dan tren penjualan",
        "class": DashboardPage,
    },
    "products": {
        "title": "Manajemen Data Produk",
        "subtitle": "Kelola katalog produk, harga modal, harga jual, dan batas stok minimum",
        "class": ProductsPage,
    },
    "suppliers": {
        "title": "Pemasok (Suppliers)",
        "subtitle": "Kelola data mitra pemasok bahan baku dan barang dagang",
        "class": SuppliersPage,
    },
    "transactions": {
        "title": "Transaksi Persediaan",
        "subtitle": "Catat arus barang masuk (pembelian) dan barang keluar (penyesuaian)",
        "class": TransactionsPage,
    },
    "sales": {
        "title": "Riwayat Penjualan",
        "subtitle": "Catat transaksi penjualan konsumen dan pantau total pendapatan",
        "class": SalesPage,
    },
    "inventory_analysis": {
        "title": "Optimasi Persediaan (EOQ & ROP)",
        "subtitle": "Kalkulasi otomatis Economic Order Quantity, Safety Stock, dan titik pemesanan kembali",
        "class": InventoryAnalysisPage,
    },
    "forecasting": {
        "title": "Peramalan Permintaan (Forecasting)",
        "subtitle": "Model estimasi permintaan menggunakan Moving Average dan Exponential Smoothing",
        "class": ForecastingPage,
    },
    "reports": {
        "title": "Laporan & Valuasi Persediaan",
        "subtitle": "Tinjauan valuasi aset stok, ekspor laporan teks, dan visualisasi grafik",
        "class": ReportsPage,
    },
    "import_export": {
        "title": "Layanan Impor & Ekspor CSV",
        "subtitle": "Pertukaran data massal antara PostgreSQL dan file CSV menggunakan Pandas",
        "class": ImportExportPage,
    },
}


class SmartStockApp(tk.Tk):
    """
    Jendela Utama Aplikasi Desktop SmartStock GUI.
    """

    def __init__(self):
        super().__init__()
        self.title("SmartStock - Sistem Manajemen & Optimasi Persediaan")
        self.geometry("1160x720")
        self.minsize(980, 620)
        self.configure(bg=BG_MAIN)

        self._atur_gaya_ttk()

        # Layout Utama: Kiri (Sidebar), Kanan (Header + Page Container)
        self.bilah_samping = Sidebar(self, saat_navigasi=self.tampilkan_halaman)
        self.bilah_samping.pack(side="left", fill="y")

        self.wadah_kanan = tk.Frame(self, bg=BG_MAIN)
        self.wadah_kanan.pack(side="right", fill="both", expand=True)

        self.bilah_atas = Header(
            self.wadah_kanan,
            title="Dasbor Utama",
            subtitle="Pantau metrik persediaan, peringatan stok, dan tren penjualan",
            saat_muat_ulang=self._saat_muat_ulang_header,
        )
        self.bilah_atas.pack(fill="x")

        # Container Halaman Konten
        self.wadah_halaman = tk.Frame(self.wadah_kanan, bg=BG_MAIN)
        self.wadah_halaman.pack(fill="both", expand=True)

        self.daftar_halaman: Dict[str, tk.Frame] = {}
        self.kunci_halaman_aktif: str = ""

        # Muat halaman default (dashboard)
        self.tampilkan_halaman("dashboard")

    def _atur_gaya_ttk(self):
        """Mengatur gaya visual ttk agar senada dengan desain modern."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Treeview (Data Table)
        style.configure(
            "Treeview",
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_CARD,
            rowheight=30,
            font=FONT_BODY,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground=TEXT_SECONDARY,
            font=FONT_BODY_BOLD,
            relief="flat",
            padding=(6, 6),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#EEF2FF")],
            foreground=[("active", ACCENT_PRIMARY)],
        )
        style.map(
            "Treeview",
            background=[("selected", "#EEF2FF")],
            foreground=[("selected", ACCENT_PRIMARY)],
        )

        # Scrollbar
        style.configure(
            "TScrollbar",
            gripcount=0,
            background="#E2E8F0",
            darkcolor="#CBD5E1",
            lightcolor="#F1F5F9",
            troughcolor="#F8FAFC",
            bordercolor="#E2E8F0",
            arrowcolor=TEXT_SECONDARY,
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground="#F8FAFC",
            background="#FFFFFF",
            font=FONT_BODY,
            padding=4,
        )

    def tampilkan_halaman(self, page_key: str):
        """Berpindah ke halaman tertentu."""
        if page_key not in PAGE_INFO:
            return

        # Sembunyikan halaman yang sedang aktif
        if self.kunci_halaman_aktif and self.kunci_halaman_aktif in self.daftar_halaman:
            self.daftar_halaman[self.kunci_halaman_aktif].pack_forget()

        # Inisialisasi halaman jika belum pernah dibuka
        if page_key not in self.daftar_halaman:
            page_class = PAGE_INFO[page_key]["class"]
            page_instance = page_class(self.wadah_halaman)
            self.daftar_halaman[page_key] = page_instance

        # Tampilkan halaman target
        page = self.daftar_halaman[page_key]
        page.pack(fill="both", expand=True)
        self.kunci_halaman_aktif = page_key

        # Sinkronkan Sidebar dan Header
        self.bilah_samping.atur_menu_aktif(page_key)
        info = PAGE_INFO[page_key]
        self.bilah_atas.perbarui_header(info["title"], info["subtitle"])

        # Panggil refresh jika halaman mendukung
        if hasattr(page, "muat_ulang") and callable(getattr(page, "muat_ulang")):
            page.muat_ulang()

    def _saat_muat_ulang_header(self):
        """Callback ketika tombol Muat Ulang di header diklik."""
        if self.kunci_halaman_aktif and self.kunci_halaman_aktif in self.daftar_halaman:
            page = self.daftar_halaman[self.kunci_halaman_aktif]
            if hasattr(page, "muat_ulang") and callable(getattr(page, "muat_ulang")):
                page.muat_ulang()


def jalankan_gui():
    """Fungsi pembuka GUI untuk dipanggil dari main.py."""
    app = SmartStockApp()
    app.mainloop()


if __name__ == "__main__":
    jalankan_gui()
