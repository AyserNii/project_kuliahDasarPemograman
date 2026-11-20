import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict
from gui.theme import (
    BG_CARD,
    BG_MAIN,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    TEXT_LIGHT,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_SUCCESS,
)
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from gui.components.dialog import SaleDialog
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan


class SalesPage(tk.Frame):
    """
    Halaman Riwayat & Pencatatan Penjualan Produk.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_penjualan = RepositoriPenjualan()
        self.repositori_produk = RepositoriProduk()

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Baris Stat Cards Penjualan
        stats_frame = tk.Frame(self, bg=BG_MAIN)
        stats_frame.pack(fill="x", pady=(0, 14))

        self.kartu_total_transaksi = StatCard(
            stats_frame,
            title="Total Transaksi",
            value="0",
            badge_text="Sales",
            badge_color=ACCENT_PRIMARY,
        )
        self.kartu_total_transaksi.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_total_kuantitas = StatCard(
            stats_frame,
            title="Volume Terjual",
            value="0 unit",
            badge_text="Volume",
            badge_color=ACCENT_SUCCESS,
            badge_bg="#ECFDF5",
        )
        self.kartu_total_kuantitas.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_total_pendapatan = StatCard(
            stats_frame,
            title="Total Pendapatan",
            value="Rp 0",
            badge_text="Revenue",
            badge_color=ACCENT_PRIMARY,
        )
        self.kartu_total_pendapatan.pack(side="left", fill="both", expand=True)

        # 2. Toolbar Tombol Aksi
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 12))

        self.tombol_penjualan = tk.Button(
            toolbar,
            text="+ Catat Penjualan Baru",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._buka_dialog_penjualan,
        )
        self.tombol_penjualan.pack(side="left")

        # 3. Tabel Riwayat Penjualan
        columns = [
            ("id_penjualan", "ID", 50, "center"),
            ("kode_transaksi", "Kode Transaksi", 130, "w"),
            ("waktu", "Waktu Penjualan", 120, "center"),
            ("sku", "SKU", 85, "w"),
            ("nama_produk", "Nama Produk", 180, "w"),
            ("jumlah_terjual", "Qty Terjual", 80, "e"),
            ("harga_satuan", "Harga Jual", 95, "e"),
            ("total", "Total Pendapatan", 110, "e"),
            ("catatan", "Catatan", 150, "w"),
        ]

        self.tabel = DataTable(
            self,
            columns=columns,
            show_search=True,
            search_placeholder="Cari transaksi, SKU, produk...",
        )
        self.tabel.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            daftar_penjualan = self.repositori_penjualan.ambil_semua(batas=500)
            jumlah_kuantitas = 0.0
            jumlah_pendapatan = 0.0
            data_terformat = []

            for s in daftar_penjualan:
                kuantitas = float(s["kuantitas_terjual"])
                price = float(s["harga_satuan"])
                jumlah_sementara = kuantitas * price
                jumlah_kuantitas += kuantitas
                jumlah_pendapatan += jumlah_sementara

                waktu = s.get("tanggal_penjualan")
                waktu_teks = waktu.strftime("%Y-%m-%d %H:%M") if waktu else "-"

                data_terformat.append({
                    "id_penjualan": s["id_penjualan"],
                    "kode_transaksi": s["kode_transaksi"],
                    "waktu": waktu_teks,
                    "sku": s.get("sku", "-"),
                    "nama_produk": s.get("nama_produk", "-"),
                    "jumlah_terjual": f"{kuantitas:.2f}",
                    "harga_satuan": f"Rp {price:,.0f}",
                    "total": f"Rp {jumlah_sementara:,.0f}",
                    "catatan": s.get("catatan") or "-",
                    "status": "AMAN",
                })

            self.kartu_total_transaksi.perbarui_nilai(f"{len(daftar_penjualan):,}")
            self.kartu_total_kuantitas.perbarui_nilai(f"{jumlah_kuantitas:,.1f} unit")
            self.kartu_total_pendapatan.perbarui_nilai(f"Rp {jumlah_pendapatan:,.0f}")
            self.tabel.atur_data(data_terformat)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Penjualan", str(kesalahan), parent=self)

    def _buka_dialog_penjualan(self):
        daftar_produk = self.repositori_produk.ambil_semua()
        if not daftar_produk:
            messagebox.showwarning("Perhatian", "Belum ada produk yang terdaftar.", parent=self)
            return

        SaleDialog(self, daftar_produk=daftar_produk, saat_simpan=self._simpan_penjualan)

    def _simpan_penjualan(self, data: Dict[str, Any]):
        self.repositori_penjualan.catat_penjualan(
            id_produk=data["id_produk"],
            kuantitas_terjual=data["jumlah_terjual"],
            harga_satuan=data["harga_satuan"],
            catatan=data["catatan"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", "Transaksi penjualan berhasil dicatat!", parent=self)
