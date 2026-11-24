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
    FONT_STAT_VAL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
)
from gui.components.stat_card import StatCard
from gui.components.chart import BarChart
from modules.forecasting import buat_peramalan_regresi_linear
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan


class ForecastingPage(tk.Frame):
    """
    Halaman Peramalan Permintaan (Demand Forecasting):
    - Regresi linear Least Squares untuk proyeksi permintaan tahunan tiga periode
    - Visualisasi permintaan tahunan hasil peramalan
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_produk = RepositoriProduk()
        self.repositori_penjualan = RepositoriPenjualan()
        self.daftar_produk: List[Dict[str, Any]] = []

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Baris Pemilihan Produk
        top_bar = tk.Frame(self, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_bar.pack(fill="x", pady=(0, 16))

        lbl_select = tk.Label(
            top_bar,
            text="Pilih Produk untuk Dianalisis:",
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        lbl_select.pack(side="left", padx=(0, 10))

        self.pilihan_produk = ttk.Combobox(top_bar, font=FONT_BODY, width=40, state="readonly")
        self.pilihan_produk.pack(side="left", padx=(0, 12))
        self.pilihan_produk.bind("<<ComboboxSelected>>", self._saat_produk_dipilih)

        btn_calc = tk.Button(
            top_bar,
            text="Hitung Ramalan",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F1F5F9",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self._hitung_peramalan,
        )
        btn_calc.pack(side="left")

        # 2. Baris Kartu Hasil Ramalan
        self.wadah_kartu = tk.Frame(self, bg=BG_MAIN)
        self.wadah_kartu.pack(fill="x", pady=(0, 16))

        self.kartu_peramalan_1 = StatCard(
            self.wadah_kartu,
            title="Peramalan Tahun ke-1",
            value="-",
            badge_text="T+1",
            badge_color=ACCENT_PRIMARY,
        )
        self.kartu_peramalan_1.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_peramalan_2 = StatCard(
            self.wadah_kartu,
            title="Peramalan Tahun ke-2",
            value="-",
            badge_text="T+2",
            badge_color=ACCENT_SUCCESS,
            badge_bg="#ECFDF5",
        )
        self.kartu_peramalan_2.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_peramalan_3 = StatCard(
            self.wadah_kartu,
            title="Peramalan Tahun ke-3",
            value="-",
            badge_text="T+3",
            badge_color=ACCENT_WARNING,
            badge_bg="#FFFBEB",
        )
        self.kartu_peramalan_3.pack(side="left", fill="both", expand=True)

        # 3. Baris Ringkasan Statistik Permintaan
        self.wadah_statistik = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        self.wadah_statistik.pack(fill="x", pady=(0, 16))

        self.label_statistik = tk.Label(
            self.wadah_statistik,
            text="Pilih produk di atas untuk melihat tren permintaan dan proyeksi tahunan.",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            justify="left",
            anchor="w",
        )
        self.label_statistik.pack(fill="x")

        # 4. Grafik Penjualan Historis
        self.grafik = BarChart(
            self,
            title="Peramalan Permintaan Tahunan (Unit)",
            width=800,
            height=200,
        )
        self.grafik.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            self.daftar_produk = self.repositori_produk.ambil_semua()
            opsi = [f"{p['sku']} - {p['nama']}" for p in self.daftar_produk]
            self.pilihan_produk["values"] = opsi
            if opsi:
                self.pilihan_produk.current(0)
                self._hitung_peramalan()
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Produk", str(kesalahan), parent=self)

    def _saat_produk_dipilih(self, peristiwa):
        self._hitung_peramalan()

    def _hitung_peramalan(self):
        indeks = self.pilihan_produk.current()
        if indeks < 0 or indeks >= len(self.daftar_produk):
            return

        produk = self.daftar_produk[indeks]
        id_produk = produk["id_produk"]

        penjualan_tahunan = self.repositori_penjualan.ambil_permintaan_tahunan(id_produk)
        if not penjualan_tahunan:
            self.kartu_peramalan_1.perbarui_nilai("-")
            self.kartu_peramalan_2.perbarui_nilai("-")
            self.kartu_peramalan_3.perbarui_nilai("-")
            self.label_statistik.config(
                text=f"Produk '{produk['nama']}' belum memiliki riwayat penjualan.\n"
                "Catat penjualan untuk mengaktifkan peramalan regresi tahunan."
            )
            self.grafik.atur_data([], [])
            return

        hasil_peramalan = buat_peramalan_regresi_linear(penjualan_tahunan)
        kartu_peramalan = (
            self.kartu_peramalan_1,
            self.kartu_peramalan_2,
            self.kartu_peramalan_3,
        )
        for kartu, ramalan in zip(kartu_peramalan, hasil_peramalan["ramalan"]):
            kartu.perbarui_nilai(
                f"{ramalan['permintaan_tahunan']:,.1f} unit/tahun",
                new_badge=str(ramalan["tahun"]),
            )

        teks_ringkasan = (
            f"Regresi Least Squares untuk {produk['nama']} (SKU: {produk['sku']}):\n"
            f"• Periode historis: {len(hasil_peramalan['historis'])} tahun\n"
            f"• Garis regresi: {hasil_peramalan['persamaan']}\n"
            "• Permintaan tahunan diproyeksikan untuk tiga tahun berikutnya."
        )
        self.label_statistik.config(text=teks_ringkasan)

        label_grafik = [str(baris["tahun"]) for baris in hasil_peramalan["ramalan"]]
        nilai_grafik = [
            float(baris["permintaan_tahunan"])
            for baris in hasil_peramalan["ramalan"]
        ]
        self.grafik.atur_data(label_grafik, nilai_grafik)
