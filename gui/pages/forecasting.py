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
from modules.forecasting import (
    hitung_statistik_permintaan,
    rata_rata_bergerak,
    pemulusan_eksponensial,
)
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan


class ForecastingPage(tk.Frame):
    """
    Halaman Peramalan Permintaan (Demand Forecasting):
    - Moving Average (3 & 7 periode)
    - Single Exponential Smoothing (SES)
    - Visualisasi deret penjualan aktual vs ramalan
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

        self.kartu_rata_rata_3 = StatCard(
            self.wadah_kartu,
            title="Moving Avg (3 Periode)",
            value="-",
            badge_text="MA-3",
            badge_color=ACCENT_PRIMARY,
        )
        self.kartu_rata_rata_3.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_rata_rata_7 = StatCard(
            self.wadah_kartu,
            title="Moving Avg (7 Periode)",
            value="-",
            badge_text="MA-7",
            badge_color=ACCENT_SUCCESS,
            badge_bg="#ECFDF5",
        )
        self.kartu_rata_rata_7.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_pemulusan_eksponensial = StatCard(
            self.wadah_kartu,
            title="Exp. Smoothing (α=0.3)",
            value="-",
            badge_text="SES",
            badge_color=ACCENT_WARNING,
            badge_bg="#FFFBEB",
        )
        self.kartu_pemulusan_eksponensial.pack(side="left", fill="both", expand=True)

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
            text="Pilih produk di atas untuk melihat ringkasan historis permintaan harian.",
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
            title="Riwayat Volume Penjualan Aktual (Unit)",
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

        penjualan_harian = self.repositori_penjualan.ambil_penjualan_harian(id_produk, hari=90)
        if not penjualan_harian:
            self.kartu_rata_rata_3.perbarui_nilai("0 unit")
            self.kartu_rata_rata_7.perbarui_nilai("0 unit")
            self.kartu_pemulusan_eksponensial.perbarui_nilai("0 unit")
            self.label_statistik.config(
                text=f"Produk '{produk['nama']}' belum memiliki riwayat penjualan dalam 90 hari terakhir.\n"
                f"Catat penjualan baru di menu Penjualan untuk mengaktifkan model peramalan otomatis."
            )
            self.grafik.atur_data([], [])
            return

        daftar_kuantitas = [float(baris["total_kuantitas"]) for baris in penjualan_harian]
        stats = hitung_statistik_permintaan(daftar_kuantitas)

        rata_rata_3 = rata_rata_bergerak(daftar_kuantitas, ukuran_jendela=3)
        rata_rata_7 = rata_rata_bergerak(daftar_kuantitas, ukuran_jendela=7)
        nilai_pemulusan = pemulusan_eksponensial(daftar_kuantitas, alfa=0.3)

        self.kartu_rata_rata_3.perbarui_nilai(f"{rata_rata_3:.2f} unit/hari")
        self.kartu_rata_rata_7.perbarui_nilai(f"{rata_rata_7:.2f} unit/hari")
        self.kartu_pemulusan_eksponensial.perbarui_nilai(f"{nilai_pemulusan:.2f} unit/hari")

        teks_ringkasan = (
            f"Statistik Permintaan untuk {produk['nama']} (SKU: {produk['sku']}):\n"
            f"• Jumlah Hari Transaksi: {len(daftar_kuantitas)} hari\n"
            f"• Rata-rata Penjualan Harian: {stats['rata_rata_harian']:.2f} unit/hari\n"
            f"• Standar Deviasi Permintaan: {stats['standar_deviasi_harian']:.2f}\n"
            f"• Estimasi Permintaan Tahunan: {stats['proyeksi_tahunan']:,.0f} unit/tahun"
        )
        self.label_statistik.config(text=teks_ringkasan)

        # Update Grafik
        tanggal_grafik = [str(baris["hari_penjualan"])[5:] for baris in penjualan_harian[-10:]]
        nilai_grafik = [float(baris["total_kuantitas"]) for baris in penjualan_harian[-10:]]
        self.grafik.atur_data(tanggal_grafik, nilai_grafik)
