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
    TEXT_LIGHT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_DANGER,
)
from gui.components.data_table import DataTable
from gui.components.dialog import ProductDialog
from repositories.product_repository import RepositoriProduk
from repositories.supplier_repository import RepositoriPemasok


class ProductsPage(tk.Frame):
    """
    Halaman Manajemen Data Produk:
    - Tabel interaktif seluruh produk dengan pencarian live
    - Tambah, Edit, Hapus produk langsung tersinkron ke PostgreSQL
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_produk = RepositoriProduk()
        self.repositori_pemasok = RepositoriPemasok()

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        # 1. Baris Toolbar Atas: Tombol Aksi
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 14))

        self.tombol_tambah = tk.Button(
            toolbar,
            text="+ Tambah Produk Baru",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._tambah_produk,
        )
        self.tombol_tambah.pack(side="left", padx=(0, 8))

        self.tombol_ubah = tk.Button(
            toolbar,
            text="✏️ Edit Produk",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._ubah_produk,
        )
        self.tombol_ubah.pack(side="left", padx=(0, 8))

        self.tombol_hapus = tk.Button(
            toolbar,
            text="🗑️ Hapus",
            font=FONT_BODY,
            fg=ACCENT_DANGER,
            bg=BG_CARD,
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._hapus_produk,
        )
        self.tombol_hapus.pack(side="left")

        # 2. Tabel Data Produk
        columns = [
            ("id_produk", "ID", 50, "center"),
            ("sku", "SKU", 90, "w"),
            ("nama", "Nama Produk", 180, "w"),
            ("kategori", "Kategori", 100, "w"),
            ("nama_pemasok", "Pemasok", 130, "w"),
            ("satuan", "Satuan", 60, "center"),
            ("jumlah_stok", "Stok", 70, "e"),
            ("biaya_satuan", "Harga Modal", 90, "e"),
            ("harga_jual", "Harga Jual", 90, "e"),
            ("stok_minimum", "Min. Stok", 75, "e"),
            ("status", "Status", 90, "center"),
        ]

        self.tabel = DataTable(
            self,
            columns=columns,
            show_search=True,
            search_placeholder="Cari SKU, nama, kategori, pemasok...",
            saat_klik_ganda=lambda baris: self._ubah_produk(),
        )
        self.tabel.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            daftar_produk = self.repositori_produk.ambil_semua()
            data_terformat = []
            for p in daftar_produk:
                stok = float(p.get("jumlah_stok", 0))
                stok_minimum = float(p.get("stok_minimum", 0))

                if stok <= 0:
                    status = "HABIS"
                elif stok <= stok_minimum:
                    status = "REORDER"
                else:
                    status = "AMAN"

                data_terformat.append({
                    "id_produk": p["id_produk"],
                    "sku": p["sku"],
                    "nama": p["nama"],
                    "kategori": p.get("kategori") or "-",
                    "nama_pemasok": p.get("nama_pemasok") or "-",
                    "satuan": p.get("satuan", "pcs"),
                    "jumlah_stok": f"{stok:.1f}",
                    "biaya_satuan": f"Rp {float(p.get('biaya_satuan', 0)):,.0f}",
                    "harga_jual": f"Rp {float(p.get('harga_jual', 0)):,.0f}",
                    "stok_minimum": f"{stok_minimum:.1f}",
                    "status": status,
                    # simpan data mentah untuk dialog edit
                    "_raw": p,
                })

            self.tabel.atur_data(data_terformat)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Produk", str(kesalahan), parent=self)

    def _tambah_produk(self):
        daftar_pemasok = self.repositori_pemasok.ambil_semua()
        dialog = ProductDialog(
            self,
            daftar_pemasok=daftar_pemasok,
            saat_simpan=self._simpan_produk_baru,
        )

    def _simpan_produk_baru(self, data: Dict[str, Any]):
        self.repositori_produk.buat(
            sku=data["sku"],
            nama=data["nama"],
            kategori=data["kategori"],
            id_pemasok=data["id_pemasok"],
            satuan=data["satuan"],
            jumlah_stok=data["jumlah_stok"],
            biaya_satuan=data["biaya_satuan"],
            harga_jual=data["harga_jual"],
            stok_minimum=data["stok_minimum"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", f"Produk '{data['nama']}' berhasil ditambahkan!", parent=self)

    def _ubah_produk(self):
        terpilih = self.tabel.ambil_baris_terpilih()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin diedit terlebih dahulu.", parent=self)
            return

        produk_mentah = terpilih.get("_raw", {})
        daftar_pemasok = self.repositori_pemasok.ambil_semua()

        ProductDialog(
            self,
            daftar_pemasok=daftar_pemasok,
            produk=produk_mentah,
            saat_simpan=lambda data: self._simpan_perubahan_produk(produk_mentah["id_produk"], data),
        )

    def _simpan_perubahan_produk(self, product_id: int, data: Dict[str, Any]):
        self.repositori_produk.perbarui(
            id_produk=product_id,
            nama=data["nama"],
            kategori=data["kategori"],
            id_pemasok=data["id_pemasok"],
            satuan=data["satuan"],
            biaya_satuan=data["biaya_satuan"],
            harga_jual=data["harga_jual"],
            stok_minimum=data["stok_minimum"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", "Data produk berhasil diperbarui!", parent=self)

    def _hapus_produk(self):
        terpilih = self.tabel.ambil_baris_terpilih()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin dihapus terlebih dahulu.", parent=self)
            return

        id_produk = terpilih["id_produk"]
        nama_produk = terpilih["nama"]

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus produk '{nama_produk}' (ID: {id_produk})?",
            parent=self,
        )
        if konfirmasi:
            try:
                jumlah_berhasil = self.repositori_produk.hapus(id_produk)
                if jumlah_berhasil:
                    self.muat_ulang()
                    messagebox.showinfo("Sukses", "Produk berhasil dihapus.", parent=self)
                else:
                    messagebox.showerror("Gagal", "Produk tidak dapat dihapus.", parent=self)
            except Exception as kesalahan:
                messagebox.showerror("Gagal Menghapus", str(kesalahan), parent=self)
