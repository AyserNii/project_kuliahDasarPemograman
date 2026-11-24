import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from gui.app import PAGE_INFO, SmartStockApp
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
from gui.components.chart import DonutChart
from gui.components.dialog import TransactionDialog


class TestGUINavigationAndPages(unittest.TestCase):
    """Pengujian terfokus untuk modul GUI tanpa memerlukan server display fisik."""

    def test_page_info_contains_all_required_pages(self):
        required_pages = [
            "dashboard",
            "products",
            "suppliers",
            "transactions",
            "sales",
            "inventory_analysis",
            "forecasting",
            "import_export",
            "reports",
        ]
        for page_key in required_pages:
            self.assertIn(page_key, PAGE_INFO)
            self.assertIn("title", PAGE_INFO[page_key])
            self.assertIn("class", PAGE_INFO[page_key])

    @patch("modules.cli_menu.jalankan_cli")
    def test_main_cli_flag_invokes_cli(self, mock_cli):
        from main import jalankan_utama

        original_argv = list(sys.argv)
        try:
            sys.argv = ["main.py", "--cli"]
            jalankan_utama()
            mock_cli.assert_called_once()
        finally:
            sys.argv = original_argv

    @patch("gui.app.jalankan_gui")
    def test_main_default_invokes_gui(self, mock_gui):
        from main import jalankan_utama

        original_argv = list(sys.argv)
        try:
            sys.argv = ["main.py"]
            jalankan_utama()
            mock_gui.assert_called_once()
        finally:
            sys.argv = original_argv

    @patch("tkinter.Tk")
    def test_app_page_navigation(self, mock_tk):
        """Memverifikasi peralihan halaman pada SmartStockApp."""
        with patch.object(SmartStockApp, "_atur_gaya_ttk"):
            with patch("gui.sidebar.Sidebar") as mock_sidebar_cls:
                with patch("gui.header.Header") as mock_header_cls:
                    with patch("gui.app.DashboardPage", return_value=MagicMock()):
                        app = SmartStockApp()
                        app.bilah_samping = MagicMock()
                        app.bilah_atas = MagicMock()

                        # Navigasi ke halaman produk
                        mock_prod_page = MagicMock()
                        with patch("gui.pages.products.ProductsPage", return_value=mock_prod_page):
                            app.tampilkan_halaman("products")
                            self.assertEqual(app.kunci_halaman_aktif, "products")
                            app.bilah_samping.atur_menu_aktif.assert_called_with("products")
                            app.bilah_atas.perbarui_header.assert_called_with(
                                PAGE_INFO["products"]["title"],
                                PAGE_INFO["products"]["subtitle"],
                            )

    def test_dashboard_uses_sales_repository_schema(self):
        dasbor = SimpleNamespace(
            repositori_produk=MagicMock(),
            repositori_penjualan=MagicMock(),
            kartu_total_produk=MagicMock(),
            kartu_stok_tersedia=MagicMock(),
            kartu_stok_menipis=MagicMock(),
            kartu_stok_habis=MagicMock(),
            grafik_donat=MagicMock(),
            grafik_batang=MagicMock(),
            tabel_peringatan=MagicMock(),
        )
        dasbor.repositori_produk.ambil_semua.return_value = []
        dasbor.repositori_penjualan.ambil_semua.return_value = [
            {"sku": "BRG-1", "kuantitas_terjual": 3}
        ]

        DashboardPage.muat_ulang(dasbor)

        dasbor.repositori_penjualan.ambil_semua.assert_called_once_with(batas=30)
        dasbor.grafik_batang.atur_data.assert_called_once_with(["BRG-1"], [3.0])

    def test_dashboard_donut_chart_has_required_theme_names(self):
        grafik = SimpleNamespace(
            kanvas=MagicMock(),
            wadah_legenda=MagicMock(),
            lebar_grafik=340,
        )

        with patch("gui.components.chart.tk.Frame"), patch("gui.components.chart.tk.Label"):
            DonutChart.atur_data(grafik, {"Aman": (2, "#10B981")})

    def test_new_product_save_uses_repository_sku_argument(self):
        halaman = SimpleNamespace(
            repositori_produk=MagicMock(),
            muat_ulang=MagicMock(),
        )
        data = {
            "sku": "BRG-1",
            "nama": "Produk",
            "kategori": None,
            "id_pemasok": None,
            "satuan": "pcs",
            "jumlah_stok": 4,
            "biaya_satuan": 1000,
            "harga_jual": 1500,
            "stok_minimum": 1,
        }

        with patch("gui.pages.products.messagebox.showinfo"):
            ProductsPage._simpan_produk_baru(halaman, data)

        halaman.repositori_produk.buat.assert_called_once_with(
            sku="BRG-1",
            nama="Produk",
            kategori=None,
            id_pemasok=None,
            satuan="pcs",
            jumlah_stok=4,
            biaya_satuan=1000,
            harga_jual=1500,
            stok_minimum=1,
        )

    def test_transaction_dialog_uses_cli_field_names(self):
        produk = {"id_produk": 8, "id_pemasok": 3}
        dialog = SimpleNamespace(
            masukan_produk=MagicMock(),
            peta_produk={"BRG-8 - Produk": produk},
            masukan_jenis=MagicMock(),
            masukan_kuantitas=MagicMock(),
            masukan_biaya=MagicMock(),
            masukan_catatan=MagicMock(),
            saat_simpan=MagicMock(),
            destroy=MagicMock(),
        )
        dialog.masukan_produk.ambil_nilai.return_value = "BRG-8 - Produk"
        dialog.masukan_jenis.ambil_nilai.return_value = "IN (Barang Masuk / Pembelian)"
        dialog.masukan_kuantitas.ambil_nilai.return_value = "3"
        dialog.masukan_biaya.ambil_nilai.return_value = "2500"
        dialog.masukan_catatan.ambil_nilai.return_value = "Restok"

        TransactionDialog._saat_disimpan(dialog)

        dialog.saat_simpan.assert_called_once_with(
            {
                "id_produk": 8,
                "jenis_transaksi": "IN",
                "kuantitas": 3.0,
                "biaya_satuan": 2500.0,
                "id_pemasok": 3,
                "catatan": "Restok",
            }
        )

    def test_transaction_save_uses_repository_and_cli_argument_names(self):
        halaman = SimpleNamespace(
            repositori_transaksi=MagicMock(),
            muat_ulang=MagicMock(),
        )
        data = {
            "id_produk": 8,
            "jenis_transaksi": "IN",
            "kuantitas": 3,
            "biaya_satuan": 2500,
            "id_pemasok": 3,
            "catatan": "Restok",
        }

        with patch("gui.pages.transactions.messagebox.showinfo"):
            TransactionsPage._simpan_transaksi(halaman, "IN", data)

        panggilan = halaman.repositori_transaksi.buat.call_args.kwargs
        self.assertRegex(panggilan["kode_transaksi"], r"^TXN-IN-\d{14}$")
        self.assertEqual(
            {k: v for k, v in panggilan.items() if k != "kode_transaksi"},
            data,
        )

    def test_sales_history_uses_repository_fields_and_limit_name(self):
        riwayat = SimpleNamespace(
            repositori_penjualan=MagicMock(),
            kartu_total_transaksi=MagicMock(),
            kartu_total_kuantitas=MagicMock(),
            kartu_total_pendapatan=MagicMock(),
            tabel=MagicMock(),
        )
        riwayat.repositori_penjualan.ambil_semua.return_value = [
            {
                "id_penjualan": 1,
                "kode_transaksi": "SALE-1",
                "tanggal_penjualan": None,
                "sku": "BRG-1",
                "nama_produk": "Produk",
                "kuantitas_terjual": 2,
                "harga_satuan": 1500,
                "catatan": None,
            }
        ]

        SalesPage.muat_ulang(riwayat)

        riwayat.repositori_penjualan.ambil_semua.assert_called_once_with(batas=500)
        baris = riwayat.tabel.atur_data.call_args.args[0][0]
        self.assertEqual(baris["jumlah_terjual"], "2.00")
        self.assertEqual(baris["waktu"], "-")

    def test_sales_save_passes_indonesian_repository_argument(self):
        halaman = SimpleNamespace(
            repositori_penjualan=MagicMock(),
            muat_ulang=MagicMock(),
        )
        data = {
            "id_produk": 7,
            "jumlah_terjual": 2,
            "harga_satuan": 1500,
            "catatan": "Penjualan",
        }

        with patch("gui.pages.sales.messagebox.showinfo"):
            SalesPage._simpan_penjualan(halaman, data)

            halaman.repositori_penjualan.catat_penjualan.assert_called_once_with(
            id_produk=7,
            kuantitas_terjual=2,
            harga_satuan=1500,
            catatan="Penjualan",
        )

    def test_forecast_uses_repository_and_cli_parameter_names(self):
        halaman = SimpleNamespace(
            pilihan_produk=MagicMock(),
            daftar_produk=[{"id_produk": 7, "sku": "BRG-1", "nama": "Produk"}],
            repositori_penjualan=MagicMock(),
            kartu_peramalan_1=MagicMock(),
            kartu_peramalan_2=MagicMock(),
            kartu_peramalan_3=MagicMock(),
            label_statistik=MagicMock(),
            grafik=MagicMock(),
        )
        halaman.pilihan_produk.current.return_value = 0
        halaman.repositori_penjualan.ambil_permintaan_tahunan.return_value = [
            {"tahun": 2025, "total_kuantitas": 20},
            {"tahun": 2026, "total_kuantitas": 30},
        ]

        ForecastingPage._hitung_peramalan(halaman)

        halaman.repositori_penjualan.ambil_permintaan_tahunan.assert_called_once_with(7)
        halaman.kartu_peramalan_1.perbarui_nilai.assert_called_once()
        halaman.kartu_peramalan_2.perbarui_nilai.assert_called_once()
        halaman.kartu_peramalan_3.perbarui_nilai.assert_called_once()
        halaman.grafik.atur_data.assert_called_once()

    def test_inventory_report_export_uses_supported_filename_argument(self):
        halaman = SimpleNamespace(
            repositori_produk=MagicMock(),
        )
        halaman.repositori_produk.ambil_semua.return_value = []

        with patch(
            "gui.pages.reports.hasilkan_laporan_ringkasan_inventaris",
            return_value="laporan",
        ), patch(
            "gui.pages.reports.simpan_laporan_teks",
            return_value="laporan.txt",
        ) as simpan_laporan, patch("gui.pages.reports.messagebox.showinfo"):
            ReportsPage._ekspor_laporan_teks(halaman)

        simpan_laporan.assert_called_once_with(
            "laporan",
            awalan_nama_berkas="laporan_inventaris",
        )


if __name__ == "__main__":
    unittest.main()
