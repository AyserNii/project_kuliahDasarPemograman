import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List
from gui.theme import (
    BG_CARD,
    BG_MAIN,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    ACCENT_DANGER,
)
from gui.components.stat_card import StatCard
from gui.components.chart import BarChart, DonutChart
from gui.components.data_table import DataTable
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan
from services.inventory_service import LayananPersediaan


class DashboardPage(tk.Frame):
    """
    Halaman Dasbor Utama:
    - 4 Kartu Metrik Ringkasan Stok & Aset
    - Diagram Batang Tren Penjualan & Diagram Donat Status Inventaris
    - Tabel Peringatan Stok Menipis / Perlu Reorder
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self.repositori_produk = RepositoriProduk()
        self.repositori_penjualan = RepositoriPenjualan()
        self.layanan_persediaan = LayananPersediaan(self.repositori_produk, self.repositori_penjualan)

        # Container scrollable agar responsif di berbagai resolusi layar
        self.kanvas_gulir = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        self.bilah_gulir = ttk.Scrollbar(self, orient="vertical", command=self.kanvas_gulir.yview)
        self.wadah_konten = tk.Frame(self.kanvas_gulir, bg=BG_MAIN, padx=24, pady=20)

        self.kanvas_gulir.create_window((0, 0), window=self.wadah_konten, anchor="nw")
        self.kanvas_gulir.configure(yscrollcommand=self.bilah_gulir.set)

        self.bilah_gulir.pack(side="right", fill="y")
        self.kanvas_gulir.pack(side="left", fill="both", expand=True)

        self.wadah_konten.bind(
            "<Configure>",
            lambda e: self.kanvas_gulir.configure(scrollregion=self.kanvas_gulir.bbox("all")),
        )

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Baris Kartu Statistik (4 Kartu)
        wadah_kartu = tk.Frame(self.wadah_konten, bg=BG_MAIN)
        wadah_kartu.pack(fill="x", pady=(0, 20))

        self.kartu_total_produk = StatCard(
            wadah_kartu,
            title="Total Produk",
            value="0",
            badge_text="Aktif",
            badge_color=ACCENT_PRIMARY,
            badge_bg="#EEF2FF",
        )
        self.kartu_total_produk.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_stok_tersedia = StatCard(
            wadah_kartu,
            title="Stok Tersedia",
            value="0 unit",
            badge_text="Aman",
            badge_color=ACCENT_SUCCESS,
            badge_bg="#ECFDF5",
        )
        self.kartu_stok_tersedia.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_stok_menipis = StatCard(
            wadah_kartu,
            title="Stok Menipis",
            value="0 item",
            badge_text="Perhatian",
            badge_color=ACCENT_WARNING,
            badge_bg="#FFFBEB",
        )
        self.kartu_stok_menipis.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_stok_habis = StatCard(
            wadah_kartu,
            title="Stok Habis",
            value="0 item",
            badge_text="Kritis",
            badge_color=ACCENT_DANGER,
            badge_bg="#FEF2F2",
        )
        self.kartu_stok_habis.pack(side="left", fill="both", expand=True)

        # 2. Baris Diagram (Bar Chart & Donut Chart)
        charts_frame = tk.Frame(self.wadah_konten, bg=BG_MAIN)
        charts_frame.pack(fill="x", pady=(0, 20))

        self.grafik_batang = BarChart(
            charts_frame,
            title="Aktivitas Penjualan Terkini (7 Periode)",
            width=540,
            height=200,
        )
        self.grafik_batang.pack(side="left", fill="both", expand=True, padx=(0, 14))

        self.grafik_donat = DonutChart(
            charts_frame,
            title="Peringatan Status Inventaris",
            width=320,
            height=200,
        )
        self.grafik_donat.pack(side="right", fill="both", expand=True)

        # 3. Baris Tabel Peringatan Stok Menipis
        table_section = tk.Frame(self.wadah_konten, bg=BG_MAIN)
        table_section.pack(fill="both", expand=True)

        lbl_section = tk.Label(
            table_section,
            text="Daftar Produk Perlu Perhatian / Reorder",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_MAIN,
            anchor="w",
        )
        lbl_section.pack(fill="x", pady=(0, 8))

        columns = [
            ("sku", "SKU", 90, "w"),
            ("nama", "Nama Produk", 200, "w"),
            ("kategori", "Kategori", 110, "w"),
            ("jumlah_stok", "Stok Fisik", 80, "e"),
            ("stok_minimum", "Batas Min", 80, "e"),
            ("status", "Status", 110, "center"),
        ]
        self.tabel_peringatan = DataTable(
            table_section,
            columns=columns,
            show_search=False,
            height=6,
        )
        self.tabel_peringatan.pack(fill="both", expand=True)

    def muat_ulang(self):
        """Memuat ulang seluruh metrik dan grafik dari database PostgreSQL."""
        try:
            daftar_produk = self.repositori_produk.ambil_semua()
            jumlah_produk = len(daftar_produk)
            jumlah_unit = sum(float(p.get("jumlah_stok", 0)) for p in daftar_produk)

            daftar_stok_menipis = []
            jumlah_stok_habis = 0
            unit_tersedia = 0

            for p in daftar_produk:
                stok = float(p.get("jumlah_stok", 0))
                stok_minimum = float(p.get("stok_minimum", 0))

                if stok <= 0:
                    jumlah_stok_habis += 1
                    status = "HABIS"
                    daftar_stok_menipis.append({**p, "status": status})
                elif stok <= stok_minimum:
                    status = "PERLU REORDER"
                    daftar_stok_menipis.append({**p, "status": status})
                else:
                    unit_tersedia += int(stok)

            # Update Stat Cards
            self.kartu_total_produk.perbarui_nilai(f"{jumlah_produk:,}")
            self.kartu_stok_tersedia.perbarui_nilai(f"{int(jumlah_unit):,} unit")
            self.kartu_stok_menipis.perbarui_nilai(f"{len(daftar_stok_menipis):,} item")
            self.kartu_stok_habis.perbarui_nilai(f"{jumlah_stok_habis:,} item")

            # Update Donut Chart
            data_donat = {
                "Aman": (float(unit_tersedia), ACCENT_SUCCESS),
                "Perlu Reorder": (float(len(daftar_stok_menipis) - jumlah_stok_habis), ACCENT_WARNING),
                "Habis": (float(jumlah_stok_habis), ACCENT_DANGER),
            }
            self.grafik_donat.atur_data(data_donat)

            # Update Bar Chart dari riwayat penjualan
            riwayat_penjualan = self.repositori_penjualan.ambil_semua(batas=30)
            if riwayat_penjualan:
                # Agregasi beberapa record terbaru
                kategori_grafik = [s["sku"] for s in riwayat_penjualan[:7]][::-1]
                nilai_grafik = [float(s["kuantitas_terjual"]) for s in riwayat_penjualan[:7]][::-1]
                self.grafik_batang.atur_data(kategori_grafik, nilai_grafik)
            else:
                # Fallback ke stok 5 produk teratas
                kategori_grafik = [p["sku"] for p in daftar_produk[:6]]
                nilai_grafik = [float(p.get("jumlah_stok", 0)) for p in daftar_produk[:6]]
                self.grafik_batang.atur_data(kategori_grafik, nilai_grafik)

            # Update Table Alerts
            self.tabel_peringatan.atur_data(daftar_stok_menipis)

        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Dasbor", str(kesalahan), parent=self)
