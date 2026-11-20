import tkinter as tk
from tkinter import messagebox
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
)
from gui.components.stat_card import StatCard
from modules.report import (
    hasilkan_laporan_ringkasan_inventaris,
    simpan_laporan_teks,
    hasilkan_grafik_stok,
)
from repositories.product_repository import RepositoriProduk


class ReportsPage(tk.Frame):
    """
    Halaman Laporan & Valuasi Inventaris:
    - Ringkasan valuasi aset persediaan
    - Simpan laporan ke format teks (.txt) di output/reports/
    - Buat visualisasi gambar grafik (.png) di output/charts/
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_produk = RepositoriProduk()

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Baris Stat Cards Valuasi
        stats_frame = tk.Frame(self, bg=BG_MAIN)
        stats_frame.pack(fill="x", pady=(0, 16))

        self.kartu_aset = StatCard(
            stats_frame,
            title="Total Nilai Aset Stok",
            value="Rp 0",
            badge_text="Valuasi",
            badge_color=ACCENT_PRIMARY,
        )
        self.kartu_aset.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_jumlah_barang = StatCard(
            stats_frame,
            title="Total Kuantitas Fisik",
            value="0 unit",
            badge_text="Fisik",
            badge_color=ACCENT_SUCCESS,
            badge_bg="#ECFDF5",
        )
        self.kartu_jumlah_barang.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.kartu_stok_menipis = StatCard(
            stats_frame,
            title="Item di Bawah Batas Min",
            value="0 item",
            badge_text="Alert",
            badge_color="#EF4444",
            badge_bg="#FEF2F2",
        )
        self.kartu_stok_menipis.pack(side="left", fill="both", expand=True)

        # 2. Toolbar Aksi Ekspor Laporan
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 14))

        self.tombol_ekspor_teks = tk.Button(
            toolbar,
            text="📄 Ekspor Laporan Teks ke output/reports/",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._ekspor_laporan_teks,
        )
        self.tombol_ekspor_teks.pack(side="left", padx=(0, 8))

        self.tombol_buat_grafik = tk.Button(
            toolbar,
            text="📊 Buat Gambar Grafik PNG ke output/charts/",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._buat_grafik_png,
        )
        self.tombol_buat_grafik.pack(side="left")

        # 3. Kotak Tinjauan Laporan (Preview)
        preview_box = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        preview_box.pack(fill="both", expand=True)

        lbl_preview = tk.Label(
            preview_box,
            text="Pratinjau Laporan Ringkasan Status Inventaris",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_preview.pack(fill="x", pady=(0, 10))

        self.teks_pratinjau = tk.Text(
            preview_box,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self.teks_pratinjau.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            daftar_produk = self.repositori_produk.ambil_semua()
            jumlah_kuantitas = sum(float(p.get("jumlah_stok", 0)) for p in daftar_produk)
            jumlah_nilai = sum(
                float(p.get("jumlah_stok", 0)) * float(p.get("biaya_satuan", 0))
                for p in daftar_produk
            )
            daftar_barang_menipis = [
                p for p in daftar_produk
                if float(p.get("jumlah_stok", 0)) <= float(p.get("stok_minimum", 0))
            ]

            self.kartu_aset.perbarui_nilai(f"Rp {jumlah_nilai:,.0f}")
            self.kartu_jumlah_barang.perbarui_nilai(f"{jumlah_kuantitas:,.1f} unit")
            self.kartu_stok_menipis.perbarui_nilai(f"{len(daftar_barang_menipis):,} item")

            # Pratinjau Teks
            content = hasilkan_laporan_ringkasan_inventaris(daftar_produk)
            self.teks_pratinjau.delete("1.0", "end")
            self.teks_pratinjau.insert("1.0", content)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Laporan", str(kesalahan), parent=self)

    def _ekspor_laporan_teks(self):
        try:
            daftar_produk = self.repositori_produk.ambil_semua()
            content = hasilkan_laporan_ringkasan_inventaris(daftar_produk)
            lokasi_berkas = simpan_laporan_teks(content, awalan_nama="laporan_inventaris")
            messagebox.showinfo("Laporan Tersimpan", f"Laporan teks berhasil disimpan di:\n{lokasi_berkas}", parent=self)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Menyimpan Laporan", str(kesalahan), parent=self)

    def _buat_grafik_png(self):
        try:
            daftar_produk = self.repositori_produk.ambil_semua()
            lokasi_berkas = hasilkan_grafik_stok(daftar_produk, nama_berkas="stok_barang.png")
            if lokasi_berkas:
                messagebox.showinfo("Grafik PNG Dibuat", f"Gambar grafik berhasil disimpan di:\n{lokasi_berkas}", parent=self)
            else:
                messagebox.showwarning(
                    "Peringatan",
                    "Library matplotlib tidak terpasang untuk merender file PNG. Grafik ditampilkan melalui kanvas GUI.",
                    parent=self,
                )
        except Exception as kesalahan:
            messagebox.showerror("Gagal Membuat Grafik", str(kesalahan), parent=self)
