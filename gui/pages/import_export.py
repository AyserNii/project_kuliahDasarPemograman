import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
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
from config.settings import IMPORTS_DIR, EXPORTS_DIR
from repositories.analysis_repository import RepositoriAnalisis
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan
from repositories.supplier_repository import RepositoriPemasok
from repositories.transaction_repository import RepositoriTransaksi
from services.export_service import LayananEkspor
from services.import_service import LayananImpor


class ImportExportPage(tk.Frame):
    """
    Halaman Layanan Impor & Ekspor Data Berformat CSV (Pandas).
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_produk = RepositoriProduk()
        self.repositori_pemasok = RepositoriPemasok()
        self.repositori_transaksi = RepositoriTransaksi()
        self.repositori_penjualan = RepositoriPenjualan()
        self.repositori_analisis = RepositoriAnalisis()

        self.layanan_impor = LayananImpor(self.repositori_produk, self.repositori_pemasok)
        self.layanan_ekspor = LayananEkspor(
            self.repositori_produk,
            self.repositori_transaksi,
            self.repositori_penjualan,
            self.repositori_analisis,
        )

        self._bangun_tampilan()

    def _bangun_tampilan(self):
        # 1. Panel Impor CSV
        box_import = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        box_import.pack(fill="x", pady=(0, 16))

        lbl_imp_title = tk.Label(
            box_import,
            text="📥 Impor Data dari Berkas CSV (Pandas)",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_imp_title.pack(fill="x")

        lbl_imp_desc = tk.Label(
            box_import,
            text="Pilih berkas CSV untuk menambahkan data produk atau pemasok secara massal ke database PostgreSQL.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_imp_desc.pack(fill="x", pady=(2, 12))

        file_row = tk.Frame(box_import, bg=BG_CARD)
        file_row.pack(fill="x", pady=(0, 12))

        self.masukan_lokasi_berkas = tk.Entry(
            file_row,
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self.masukan_lokasi_berkas.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))

        btn_browse = tk.Button(
            file_row,
            text="Pilih Berkas CSV...",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F1F5F9",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._pilih_berkas,
        )
        btn_browse.pack(side="right")

        btn_row = tk.Frame(box_import, bg=BG_CARD)
        btn_row.pack(fill="x")

        self.tombol_impor_produk = tk.Button(
            btn_row,
            text="Impor Data Produk",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._impor_produk,
        )
        self.tombol_impor_produk.pack(side="left", padx=(0, 8))

        self.tombol_impor_pemasok = tk.Button(
            btn_row,
            text="Impor Data Pemasok",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_SUCCESS,
            activebackground="#059669",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._impor_pemasok,
        )
        self.tombol_impor_pemasok.pack(side="left", padx=(0, 8))

        btn_template = tk.Button(
            btn_row,
            text="📄 Buat Templat CSV Contoh",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._buat_templat,
        )
        btn_template.pack(side="right")

        # 2. Panel Ekspor CSV
        box_export = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        box_export.pack(fill="x", pady=(0, 16))

        lbl_exp_title = tk.Label(
            box_export,
            text="📤 Ekspor Data PostgreSQL ke Berkas CSV",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_exp_title.pack(fill="x")

        lbl_exp_desc = tk.Label(
            box_export,
            text="Unduh salinan cadangan (*backup*) data atau laporan persediaan dalam format CSV yang kompatibel dengan Excel.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_exp_desc.pack(fill="x", pady=(2, 12))

        exp_buttons_row = tk.Frame(box_export, bg=BG_CARD)
        exp_buttons_row.pack(fill="x")

        btn_exp_prod = tk.Button(
            exp_buttons_row,
            text="📦 Ekspor Produk",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._ekspor_data("produk"),
        )
        btn_exp_prod.pack(side="left", padx=(0, 8))

        btn_exp_txn = tk.Button(
            exp_buttons_row,
            text="🔄 Ekspor Transaksi",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._ekspor_data("transaksi"),
        )
        btn_exp_txn.pack(side="left", padx=(0, 8))

        btn_exp_sale = tk.Button(
            exp_buttons_row,
            text="💰 Ekspor Penjualan",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._ekspor_data("penjualan"),
        )
        btn_exp_sale.pack(side="left", padx=(0, 8))

        btn_exp_ana = tk.Button(
            exp_buttons_row,
            text="📈 Ekspor Analisis EOQ",
            font=FONT_BODY,
            fg=TEXT_PRIMARY,
            bg="#F8FAFC",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._ekspor_data("analisis"),
        )
        btn_exp_ana.pack(side="left")

        # 3. Panel Log Hasil Aksi
        box_log = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        box_log.pack(fill="both", expand=True)

        lbl_log_title = tk.Label(
            box_log,
            text="📋 Status & Hasil Proses",
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        lbl_log_title.pack(fill="x")

        self.teks_log = tk.Text(
            box_log,
            height=6,
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg="#F8FAFC",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self.teks_log.pack(fill="both", expand=True, pady=(8, 0))
        self._catat_log("Layanan Impor/Ekspor siap digunakan.")

    def _catat_log(self, text: str):
        self.teks_log.insert("end", f"{text}\n")
        self.teks_log.see("end")

    def _pilih_berkas(self):
        berkas = filedialog.askopenfilename(
            initialdir=str(IMPORTS_DIR),
            filetypes=[("Berkas CSV", "*.csv"), ("Semua Berkas", "*.*")],
            parent=self,
        )
        if berkas:
            self.masukan_lokasi_berkas.delete(0, "end")
            self.masukan_lokasi_berkas.insert(0, berkas)

    def _impor_produk(self):
        teks_lokasi_berkas = self.masukan_lokasi_berkas.get().strip()
        if not teks_lokasi_berkas or not os.lokasi_berkas.exists(teks_lokasi_berkas):
            messagebox.showwarning("Peringatan", "Pilih berkas CSV yang valid terlebih dahulu.", parent=self)
            return

        try:
            jumlah_berhasil, jumlah_gagal, daftar_kesalahan = self.layanan_impor.impor_produk_dari_csv(Path(teks_lokasi_berkas))
            self._catat_log(f"[HASIL IMPOR PRODUK] Sukses: {jumlah_berhasil} baris | Gagal/Duplikat: {jumlah_gagal} baris")
            if daftar_kesalahan:
                for kesalahan in daftar_kesalahan[:5]:
                    self._catat_log(f"  • {kesalahan}")
            messagebox.showinfo(
                "Selesai Impor",
                f"Impor produk selesai!\nSukses: {jumlah_berhasil} baris\nGagal/Duplikat: {jumlah_gagal} baris",
                parent=self,
            )
        except Exception as kesalahan:
            messagebox.showerror("Gagal Impor", str(kesalahan), parent=self)

    def _impor_pemasok(self):
        teks_lokasi_berkas = self.masukan_lokasi_berkas.get().strip()
        if not teks_lokasi_berkas or not os.lokasi_berkas.exists(teks_lokasi_berkas):
            messagebox.showwarning("Peringatan", "Pilih berkas CSV yang valid terlebih dahulu.", parent=self)
            return

        try:
            jumlah_berhasil, jumlah_gagal, daftar_kesalahan = self.layanan_impor.impor_pemasok_dari_csv(Path(teks_lokasi_berkas))
            self._catat_log(f"[HASIL IMPOR PEMASOK] Sukses: {jumlah_berhasil} baris | Gagal/Duplikat: {jumlah_gagal} baris")
            if daftar_kesalahan:
                for kesalahan in daftar_kesalahan[:5]:
                    self._catat_log(f"  • {kesalahan}")
            messagebox.showinfo(
                "Selesai Impor",
                f"Impor pemasok selesai!\nSukses: {jumlah_berhasil} baris\nGagal/Duplikat: {jumlah_gagal} baris",
                parent=self,
            )
        except Exception as kesalahan:
            messagebox.showerror("Gagal Impor", str(kesalahan), parent=self)

    def _buat_templat(self):
        try:
            self.layanan_impor.buat_templat_contoh()
            self._catat_log(f"[TEMPLAT] Templat CSV produk dan pemasok berhasil dibuat di: {IMPORTS_DIR}")
            messagebox.showinfo("Sukses", f"Templat CSV berhasil dibuat di folder:\n{IMPORTS_DIR}", parent=self)
        except Exception as kesalahan:
            messagebox.showerror("Gagal", str(kesalahan), parent=self)

    def _ekspor_data(self, jenis: str):
        try:
            if jenis == "produk":
                hasil_ekspor = self.layanan_ekspor.ekspor_produk_ke_csv()
            elif jenis == "transaksi":
                hasil_ekspor = self.layanan_ekspor.ekspor_transaksi_ke_csv()
            elif jenis == "penjualan":
                hasil_ekspor = self.layanan_ekspor.ekspor_penjualan_ke_csv()
            else:
                hasil_ekspor = self.layanan_ekspor.ekspor_analisis_persediaan_ke_csv()

            self._catat_log(f"[EKSPOR BERHASIL] Berkas {jenis} tersimpan di: {hasil_ekspor}")
            messagebox.showinfo("Ekspor Berhasil", f"Berkas berhasil diekspor ke:\n{hasil_ekspor}", parent=self)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Ekspor", str(kesalahan), parent=self)
