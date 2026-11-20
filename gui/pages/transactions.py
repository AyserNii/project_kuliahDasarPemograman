from datetime import datetime
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
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_SUCCESS,
    ACCENT_DANGER,
)
from gui.components.data_table import DataTable
from gui.components.dialog import TransactionDialog
from repositories.product_repository import RepositoriProduk
from repositories.transaction_repository import RepositoriTransaksi


class TransactionsPage(tk.Frame):
    """
    Halaman Riwayat & Pencatatan Transaksi Stok (IN / OUT).
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_transaksi = RepositoriTransaksi()
        self.repositori_produk = RepositoriProduk()

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 14))

        self.tombol_stok_masuk = tk.Button(
            toolbar,
            text="+ Catat Stok Masuk (IN)",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_SUCCESS,
            activebackground="#059669",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: self._buka_dialog_transaksi("IN"),
        )
        self.tombol_stok_masuk.pack(side="left", padx=(0, 8))

        self.tombol_stok_keluar = tk.Button(
            toolbar,
            text="- Catat Stok Keluar (OUT)",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg="#D97706",
            activebackground="#B45309",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: self._buka_dialog_transaksi("OUT"),
        )
        self.tombol_stok_keluar.pack(side="left")

        columns = [
            ("kode_transaksi", "Kode Transaksi", 130, "w"),
            ("waktu", "Waktu", 120, "center"),
            ("sku", "SKU", 90, "w"),
            ("nama_produk", "Nama Produk", 180, "w"),
            ("tipe_transaksi", "Tipe", 60, "center"),
            ("jumlah", "Jumlah", 75, "e"),
            ("biaya_satuan", "Biaya Satuan", 95, "e"),
            ("nama_pemasok", "Pemasok", 120, "w"),
            ("catatan", "Catatan", 180, "w"),
        ]

        self.tabel = DataTable(
            self,
            columns=columns,
            show_search=True,
            search_placeholder="Cari kode, SKU, produk, catatan...",
        )
        self.tabel.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            daftar_transaksi = self.repositori_transaksi.ambil_semua(batas=300)
            data_terformat = []
            for t in daftar_transaksi:
                waktu = t.get("waktu_transaksi")
                waktu_teks = waktu.strftime("%Y-%m-%d %H:%M") if waktu else "-"
                data_terformat.append({
                    "kode_transaksi": t["kode_transaksi"],
                    "waktu": waktu_teks,
                    "sku": t.get("sku", "-"),
                    "nama_produk": t.get("nama_produk", "-"),
                    "tipe_transaksi": t["jenis_transaksi"],
                    "jumlah": f"{float(t['kuantitas']):.2f}",
                    "biaya_satuan": f"Rp {float(t.get('biaya_satuan', 0)):,.0f}",
                    "nama_pemasok": t.get("nama_pemasok") or "-",
                    "catatan": t.get("catatan") or "-",
                    "status": "AMAN" if t["jenis_transaksi"] == "IN" else "HABIS",
                })
            self.tabel.atur_data(data_terformat)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Transaksi", str(kesalahan), parent=self)

    def _buka_dialog_transaksi(self, jenis_pergerakan: str):
        daftar_produk = self.repositori_produk.ambil_semua()
        if not daftar_produk:
            messagebox.showwarning("Perhatian", "Belum ada produk yang terdaftar.", parent=self)
            return

        TransactionDialog(
            self,
            daftar_produk=daftar_produk,
            jenis_awal=jenis_pergerakan,
            saat_simpan=lambda data: self._simpan_transaksi(jenis_pergerakan, data),
        )

    def _simpan_transaksi(self, jenis_pergerakan: str, data: Dict[str, Any]):
        waktu_kode = datetime.now().strftime("%Y%m%d%H%M%S")
        kode_transaksi = f"TXN-{jenis_pergerakan}-{waktu_kode}"

        self.repositori_transaksi.buat(
            kode_transaksi=kode_transaksi,
            id_produk=data["id_produk"],
            jenis_transaksi=data["jenis_transaksi"],
            kuantitas=data["kuantitas"],
            biaya_satuan=data["biaya_satuan"],
            id_pemasok=data["id_pemasok"],
            catatan=data["catatan"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", f"Transaksi {kode_transaksi} berhasil disimpan!", parent=self)
