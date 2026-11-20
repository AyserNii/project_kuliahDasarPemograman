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
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_DANGER,
)
from gui.components.data_table import DataTable
from gui.components.dialog import SupplierDialog
from repositories.supplier_repository import RepositoriPemasok


class SuppliersPage(tk.Frame):
    """
    Halaman Manajemen Pemasok (Suppliers):
    - Daftar pemasok dengan pencarian live
    - Tambah, Edit, dan Hapus pemasok
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, padx=24, pady=20, **kwargs)
        self.repositori_pemasok = RepositoriPemasok()

        self._bangun_tampilan()
        self.muat_ulang()

    def _bangun_tampilan(self):
        toolbar = tk.Frame(self, bg=BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 14))

        self.tombol_tambah = tk.Button(
            toolbar,
            text="+ Tambah Pemasok Baru",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._tambah_data,
        )
        self.tombol_tambah.pack(side="left", padx=(0, 8))

        self.tombol_ubah = tk.Button(
            toolbar,
            text="✏️ Edit",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._ubah_data,
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
            command=self._hapus_data,
        )
        self.tombol_hapus.pack(side="left")

        columns = [
            ("id_pemasok", "ID", 60, "center"),
            ("kode_pemasok", "Kode", 100, "w"),
            ("nama", "Nama Perusahaan / Pemasok", 220, "w"),
            ("nama_kontak", "Kontak Person", 150, "w"),
            ("telepon", "No. Telepon", 130, "w"),
            ("alamat", "Alamat", 250, "w"),
        ]

        self.tabel = DataTable(
            self,
            columns=columns,
            show_search=True,
            search_placeholder="Cari kode, nama, kontak, alamat...",
            saat_klik_ganda=lambda baris: self._ubah_data(),
        )
        self.tabel.pack(fill="both", expand=True)

    def muat_ulang(self):
        try:
            daftar_pemasok = self.repositori_pemasok.ambil_semua()
            data_terformat = []
            for s in daftar_pemasok:
                data_terformat.append({
                    "id_pemasok": s["id_pemasok"],
                    "kode_pemasok": s["kode_pemasok"],
                    "nama": s["nama"],
                    "nama_kontak": s.get("nama_kontak") or "-",
                    "telepon": s.get("telepon") or "-",
                    "alamat": s.get("alamat") or "-",
                    "_raw": s,
                })
            self.tabel.atur_data(data_terformat)
        except Exception as kesalahan:
            messagebox.showerror("Gagal Memuat Pemasok", str(kesalahan), parent=self)

    def _tambah_data(self):
        SupplierDialog(self, saat_simpan=self._simpan_data_baru)

    def _simpan_data_baru(self, data: Dict[str, Any]):
        self.repositori_pemasok.buat(
            kode_pemasok=data["kode_pemasok"],
            nama=data["nama"],
            nama_kontak=data["nama_kontak"],
            telepon=data["telepon"],
            alamat=data["alamat"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", f"Pemasok '{data['nama']}' berhasil ditambahkan!", parent=self)

    def _ubah_data(self):
        terpilih = self.tabel.ambil_baris_terpilih()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih pemasok yang ingin diedit terlebih dahulu.", parent=self)
            return

        data_mentah = terpilih.get("_raw", {})
        SupplierDialog(
            self,
            pemasok=data_mentah,
            saat_simpan=lambda data: self._simpan_perubahan(data_mentah["id_pemasok"], data),
        )

    def _simpan_perubahan(self, supplier_id: int, data: Dict[str, Any]):
        self.repositori_pemasok.perbarui(
            id_pemasok=supplier_id,
            nama=data["nama"],
            nama_kontak=data["nama_kontak"],
            telepon=data["telepon"],
            alamat=data["alamat"],
        )
        self.muat_ulang()
        messagebox.showinfo("Sukses", "Data pemasok berhasil diperbarui!", parent=self)

    def _hapus_data(self):
        terpilih = self.tabel.ambil_baris_terpilih()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih pemasok yang ingin dihapus terlebih dahulu.", parent=self)
            return

        sup_id = terpilih["id_pemasok"]
        sup_name = terpilih["nama"]

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus pemasok '{sup_name}'?",
            parent=self,
        )
        if konfirmasi:
            try:
                jumlah_berhasil = self.repositori_pemasok.hapus(sup_id)
                if jumlah_berhasil:
                    self.muat_ulang()
                    messagebox.showinfo("Sukses", "Pemasok berhasil dihapus.", parent=self)
                else:
                    messagebox.showerror("Gagal", "Pemasok tidak dapat dihapus.", parent=self)
            except Exception as kesalahan:
                messagebox.showerror("Gagal Menghapus", str(kesalahan), parent=self)
