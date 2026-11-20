import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict
from gui.theme import (
    BG_CARD,
    BG_MAIN,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    TEXT_LIGHT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    ACCENT_DANGER,
)
from gui.components.data_table import DataTable
from repositories.analysis_repository import RepositoriAnalisis
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan
from services.inventory_service import LayananPersediaan


class InventoryAnalysisPage(tk.Frame):
    """
    Halaman Optimasi Inventaris:
    - Perhitungan otomatis EOQ, Safety Stock, dan Reorder Point (ROP)
    - Rekomendasi restock dan estimasi total biaya persediaan
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_produk = RepositoriProduk()
        self.repositori_penjualan = RepositoriPenjualan()
        self.repositori_analisis = RepositoriAnalisis()
        self.layanan_persediaan = LayananPersediaan(self.repositori_produk, self.repositori_penjualan, self.repositori_analisis)

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Toolbar Atas
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 14))

        self.tombol_analisis = tk.Button(
            toolbar,
            text="⚡ Jalankan Analisis Semua Produk",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self._jalankan_analisis_massal,
        )
        self.tombol_analisis.pack(side="left", padx=(0, 10))

        lbl_info = tk.Label(
            toolbar,
            text="* Menghitung EOQ, Safety Stock, dan ROP berbasis riwayat penjualan & parameter persediaan",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
        )
        lbl_info.pack(side="left")

        # 2. Split Area: Tabel Hasil Analisis (Kiri/Atas) & Panel Rekomendasi (Bawah)
        columns = [
            ("sku", "SKU", 85, "w"),
            ("nama_produk", "Nama Produk", 170, "w"),
            ("stok", "Stok", 70, "e"),
            ("permintaan_tahunan", "Demand/Thn", 85, "e"),
            ("eoq", "EOQ (Order)", 85, "e"),
            ("safety_stock", "Safety Stock", 85, "e"),
            ("reorder_point", "Reorder Point", 85, "e"),
            ("status", "Status", 95, "center"),
            ("tgl", "Tgl Analisis", 95, "center"),
        ]

        self.tabel = DataTable(
            self,
            columns=columns,
            show_search=True,
            search_placeholder="Cari SKU, nama produk, status...",
            saat_pilih=self._saat_item_dipilih,
        )
        self.tabel.pack(fill="both", expand=True, pady=(0, 14))

        # 3. Panel Detail Rekomendasi
        self.wadah_rincian = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        self.wadah_rincian.pack(fill="x")

        self.label_judul_rincian = tk.Label(
            self.wadah_rincian,
            text="Pilih produk dari tabel di atas untuk melihat rincian kalkulasi dan rekomendasi sistem",
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_judul_rincian.pack(fill="x")

        self.label_rincian = tk.Label(
            self.wadah_rincian,
            text="",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            anchor="w",
            justify="left",
        )
        self.label_rincian.pack(fill="x", pady=(6, 0))

    def muat_ulang(self):
        try:
            daftar_analisis = self.repositori_analisis.ambil_semua_terbaru()
            data_terformat = []
            for a in daftar_analisis:
                stok = float(a.get("jumlah_stok", 0))
                titik_pemesanan_ulang = float(a.get("titik_pemesanan_ulang", 0))
                stok_pengaman = float(a.get("stok_pengaman", 0))

                if stok <= 0:
                    status = "HABIS"
                elif stok <= titik_pemesanan_ulang:
                    status = "PERLU REORDER"
                else:
                    status = "AMAN"

                data_terformat.append({
                    "sku": a.get("sku", "-"),
                    "nama_produk": a.get("nama_produk", "-"),
                    "stok": f"{stok:.1f}",
                    "permintaan_tahunan": f"{float(a['permintaan_tahunan']):,.0f}",
                    "eoq": f"{float(a['kuantitas_pemesanan_ekonomis']):.0f}",
                    "safety_stock": f"{stok_pengaman:.1f}",
                    "reorder_point": f"{titik_pemesanan_ulang:.1f}",
                    "status": status,
                    "tgl": str(a.get("tanggal_analisis", "-")),
                    "_raw": a,
                })
            self.tabel.atur_data(data_terformat)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Analisis", str(kesalahan), parent=self)

    def _jalankan_analisis_massal(self):
        try:
            daftar_hasil = self.layanan_persediaan.analisis_semua_produk()
            self.muat_ulang()
            messagebox.showinfo(
                "Analisis Berhasil",
                f"Selesai menjalankan perhitungan optimasi inventaris untuk {len(daftar_hasil)} produk!",
                parent=self,
            )
        except Exception as kesalahan:
            messagebox.showerror("Gagal Menjalankan Analisis", str(kesalahan), parent=self)

    def _saat_item_dipilih(self, baris: Dict[str, Any]):
        a = baris.get("_raw")
        if not a:
            return

        stok = float(a.get("jumlah_stok", 0))
        kuantitas_pemesanan_ekonomis = float(a.get("kuantitas_pemesanan_ekonomis", 0))
        titik_pemesanan_ulang = float(a.get("titik_pemesanan_ulang", 0))
        stok_pengaman = float(a.get("stok_pengaman", 0))
        d = float(a.get("permintaan_tahunan", 0))
        biaya_pemesanan = float(a.get("biaya_pemesanan", 0))
        biaya_penyimpanan = float(a.get("biaya_penyimpanan_per_unit_tahun", 0))

        jumlah_pemesanan = d / kuantitas_pemesanan_ekonomis if kuantitas_pemesanan_ekonomis > 0 else 0
        hari_siklus = (kuantitas_pemesanan_ekonomis / d * 365) if d > 0 else 0

        self.label_judul_rincian.config(
            text=f"Rincian Analisis: {a['nama_produk']} (SKU: {a['sku']}) | Status: [{baris['status']}]"
        )

        detail_text = (
            f"• Kuantitas Pesan Ekonomis (EOQ): {kuantitas_pemesanan_ekonomis:.0f} unit per order\n"
            f"• Persediaan Pengaman (Safety Stock): {stok_pengaman:.1f} unit  |  Titik Pemesanan Kembali (ROP): {titik_pemesanan_ulang:.1f} unit\n"
            f"• Frekuensi Pemesanan: ~{jumlah_pemesanan:.1f} kali/tahun  (setiap ~{hari_siklus:.0f} hari)\n"
            f"• Biaya Pemesanan: Rp {biaya_pemesanan:,.0f}/order  |  Biaya Simpan: Rp {biaya_penyimpanan:,.0f}/unit/tahun\n"
            f"• Rekomendasi Tindakan: "
            + (
                f"Lakukan pemesanan ulang segera sebesar {kuantitas_pemesanan_ekonomis:.0f} unit!"
                if stok <= titik_pemesanan_ulang
                else "Stok dalam batas aman. Pertahankan tingkat persediaan."
            )
        )
        self.label_rincian.config(text=detail_text)
