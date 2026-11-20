import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Dict, List, Optional
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
from gui.components.form_input import FormField


class BaseModalDialog(tk.Toplevel):
    """Kelas dasar untuk modal dialog modern."""

    def __init__(self, parent, title: str, width: int = 480, height: int = 520):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Posisi di tengah jendela induk
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + max(0, (parent_w - width) // 2)
        y = parent_y + max(0, (parent_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Header Dialog
        header_frame = tk.Frame(self, bg=BG_CARD, padx=20, pady=16)
        header_frame.pack(fill="x")

        lbl_title = tk.Label(
            header_frame, text=title, font=FONT_HEADING, fg=TEXT_PRIMARY, bg=BG_CARD
        )
        lbl_title.pack(side="left")

        btn_close = tk.Button(
            header_frame,
            text="✕",
            font=FONT_BODY,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.destroy,
        )
        btn_close.pack(side="right")

        sep = tk.Frame(self, height=1, bg=BORDER_COLOR)
        sep.pack(fill="x")

        # Formulir digulir agar footer tetap terlihat pada dialog yang tinggi.
        body_container = tk.Frame(self, bg=BG_CARD)
        body_container.pack(fill="both", expand=True)
        canvas = tk.Canvas(body_container, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.isi_formulir = tk.Frame(canvas, bg=BG_CARD, padx=20, pady=16)
        window_id = canvas.create_window((0, 0), window=self.isi_formulir, anchor="nw")
        self.isi_formulir.bind(
            "<Configure>",
            lambda peristiwa: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda peristiwa: canvas.itemconfigure(window_id, width=peristiwa.width),
        )

        # Footer Tombol Aksi
        footer_sep = tk.Frame(self, height=1, bg=BORDER_COLOR)
        footer_sep.pack(fill="x")

        footer = tk.Frame(self, bg="#F8FAFC", padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        self.tombol_batal = tk.Button(
            footer,
            text="Batal",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg="#FFFFFF",
            relief="flat",
            bd=1,
            highlightbackground=BORDER_COLOR,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.destroy,
        )
        self.tombol_batal.pack(side="right", padx=(8, 0))

        self.tombol_simpan = tk.Button(
            footer,
            text="Simpan",
            font=FONT_BODY_BOLD,
            fg=TEXT_LIGHT,
            bg=ACCENT_PRIMARY,
            activebackground=ACCENT_PRIMARY_HOVER,
            relief="flat",
            bd=0,
            padx=16,
            pady=5,
            cursor="hand2",
            command=self._saat_disimpan,
        )
        self.tombol_simpan.pack(side="right")

        self.hasil: Optional[Dict[str, Any]] = None

    def _saat_disimpan(self):
        """Metode yang di-override oleh sub-kelas untuk validasi dan pengembalian hasil."""
        pass


class ProductDialog(BaseModalDialog):
    """Dialog Tambah/Edit Produk."""

    def __init__(
        self,
        parent,
        daftar_pemasok: List[Dict[str, Any]],
        produk: Optional[Dict[str, Any]] = None,
        saat_simpan: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.mode_ubah = produk is not None
        title = "Perbarui Data Produk" if self.mode_ubah else "Tambah Produk Baru"
        super().__init__(parent, title, width=520, height=600)
        self.daftar_pemasok = daftar_pemasok
        self.produk = produk or {}
        self.saat_simpan = saat_simpan

        # Mapping Supplier Name -> ID
        self.peta_pemasok = {
            f"{s['kode_pemasok']} - {s['nama']}": s['id_pemasok']
            for s in daftar_pemasok
        }
        sup_options = ["(Tanpa Pemasok)"] + list(self.peta_pemasok.keys())

        curr_sup_name = "(Tanpa Pemasok)"
        if self.produk.get("id_pemasok"):
            for s in daftar_pemasok:
                if s["id_pemasok"] == self.produk["id_pemasok"]:
                    curr_sup_name = f"{s['kode_pemasok']} - {s['nama']}"
                    break

        # Baris 1: SKU dan Nama
        self.masukan_sku = FormField(
            self.isi_formulir,
            label="SKU (Kode Unik Produk) *",
            default_value=self.produk.get("sku", ""),
            readonly=self.mode_ubah,
        )
        self.masukan_sku.pack(fill="x", pady=(0, 6))

        self.masukan_nama = FormField(
            self.isi_formulir,
            label="Nama Produk *",
            default_value=self.produk.get("nama", ""),
        )
        self.masukan_nama.pack(fill="x", pady=(0, 6))

        # Baris 2: Kategori dan Satuan
        row2 = tk.Frame(self.isi_formulir, bg=BG_CARD)
        row2.pack(fill="x", pady=(0, 6))

        self.masukan_kategori = FormField(
            row2,
            label="Kategori",
            default_value=self.produk.get("kategori", ""),
        )
        self.masukan_kategori.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.masukan_satuan = FormField(
            row2,
            label="Satuan",
            jenis_masukan="combobox",
            opsi=["pcs", "unit", "box", "karton", "kg", "liter", "botol", "lusin"],
            default_value=self.produk.get("satuan", "pcs"),
        )
        self.masukan_satuan.pack(side="right", fill="x", expand=True)

        # Baris 3: Pemasok
        self.masukan_pemasok = FormField(
            self.isi_formulir,
            label="Pemasok (Supplier)",
            jenis_masukan="combobox",
            opsi=sup_options,
            default_value=curr_sup_name,
            readonly=True,
        )
        self.masukan_pemasok.pack(fill="x", pady=(0, 6))

        # Baris 4: Harga Modal & Harga Jual
        row4 = tk.Frame(self.isi_formulir, bg=BG_CARD)
        row4.pack(fill="x", pady=(0, 6))

        self.masukan_biaya = FormField(
            row4,
            label="Harga Modal (Rp) *",
            default_value=str(float(self.produk.get("biaya_satuan", 0))),
        )
        self.masukan_biaya.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.masukan_harga = FormField(
            row4,
            label="Harga Jual (Rp) *",
            default_value=str(float(self.produk.get("harga_jual", 0))),
        )
        self.masukan_harga.pack(side="right", fill="x", expand=True)

        # Baris 5: Stok Awal & Stok Minimum
        row5 = tk.Frame(self.isi_formulir, bg=BG_CARD)
        row5.pack(fill="x", pady=(0, 6))

        self.masukan_stok = FormField(
            row5,
            label="Stok Fisik Saat Ini" if self.mode_ubah else "Stok Awal",
            default_value=str(float(self.produk.get("jumlah_stok", 0))),
            readonly=self.mode_ubah,  # Edit stok sebaiknya lewat menu transaksi
        )
        self.masukan_stok.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.masukan_stok_minimum = FormField(
            row5,
            label="Batas Stok Minimum *",
            default_value=str(float(self.produk.get("stok_minimum", 5))),
        )
        self.masukan_stok_minimum.pack(side="right", fill="x", expand=True)

    def _saat_disimpan(self):
        # Validasi
        kode_sku = self.masukan_sku.ambil_nilai().upper()
        nama = self.masukan_nama.ambil_nilai()

        if not kode_sku:
            self.masukan_sku.atur_pesan_kesalahan("SKU wajib diisi.")
            return
        if not nama:
            self.masukan_nama.atur_pesan_kesalahan("Nama produk wajib diisi.")
            return

        try:
            biaya = float(self.masukan_biaya.ambil_nilai() or 0)
            if biaya < 0:
                raise ValueError
        except ValueError:
            self.masukan_biaya.atur_pesan_kesalahan("Harga modal harus angka >= 0.")
            return

        try:
            harga = float(self.masukan_harga.ambil_nilai() or 0)
            if harga < 0:
                raise ValueError
        except ValueError:
            self.masukan_harga.atur_pesan_kesalahan("Harga jual harus angka >= 0.")
            return

        try:
            stok = float(self.masukan_stok.ambil_nilai() or 0)
            if stok < 0:
                raise ValueError
        except ValueError:
            self.masukan_stok.atur_pesan_kesalahan("Stok harus angka >= 0.")
            return

        try:
            min_stok = float(self.masukan_stok_minimum.ambil_nilai() or 0)
            if min_stok < 0:
                raise ValueError
        except ValueError:
            self.masukan_stok_minimum.atur_pesan_kesalahan("Stok minimum harus angka >= 0.")
            return

        selected_sup_str = self.masukan_pemasok.ambil_nilai()
        id_pemasok = self.peta_pemasok.get(selected_sup_str)

        data = {
            "sku": kode_sku,
            "nama": nama,
            "kategori": self.masukan_kategori.ambil_nilai() or None,
            "satuan": self.masukan_satuan.ambil_nilai() or "pcs",
            "id_pemasok": id_pemasok,
            "biaya_satuan": biaya,
            "harga_jual": harga,
            "jumlah_stok": stok,
            "stok_minimum": min_stok,
        }

        if self.saat_simpan:
            try:
                self.saat_simpan(data)
                self.destroy()
            except Exception as kesalahan:
                messagebox.showerror("Kesalahan", str(kesalahan), parent=self)


class SupplierDialog(BaseModalDialog):
    """Dialog Tambah/Edit Supplier."""

    def __init__(
        self,
        parent,
        pemasok: Optional[Dict[str, Any]] = None,
        saat_simpan: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.mode_ubah = pemasok is not None
        title = "Perbarui Data Pemasok" if self.mode_ubah else "Tambah Pemasok Baru"
        super().__init__(parent, title, width=460, height=480)
        self.pemasok = pemasok or {}
        self.saat_simpan = saat_simpan

        self.masukan_kode = FormField(
            self.isi_formulir,
            label="Kode Pemasok (contoh: SUP-002) *",
            default_value=self.pemasok.get("kode_pemasok", ""),
            readonly=self.mode_ubah,
        )
        self.masukan_kode.pack(fill="x", pady=(0, 6))

        self.masukan_nama = FormField(
            self.isi_formulir,
            label="Nama Perusahaan / Pemasok *",
            default_value=self.pemasok.get("nama", ""),
        )
        self.masukan_nama.pack(fill="x", pady=(0, 6))

        self.masukan_kontak = FormField(
            self.isi_formulir,
            label="Nama Kontak Person",
            default_value=self.pemasok.get("nama_kontak", ""),
        )
        self.masukan_kontak.pack(fill="x", pady=(0, 6))

        self.masukan_telepon = FormField(
            self.isi_formulir,
            label="Nomor Telepon",
            default_value=self.pemasok.get("telepon", ""),
        )
        self.masukan_telepon.pack(fill="x", pady=(0, 6))

        self.masukan_alamat = FormField(
            self.isi_formulir,
            label="Alamat Lengkap",
            jenis_masukan="textarea",
            default_value=self.pemasok.get("alamat", ""),
        )
        self.masukan_alamat.pack(fill="x", pady=(0, 6))

    def _saat_disimpan(self):
        code = self.masukan_kode.ambil_nilai().upper()
        name = self.masukan_nama.ambil_nilai()

        if not code:
            self.masukan_kode.atur_pesan_kesalahan("Kode pemasok wajib diisi.")
            return
        if not name:
            self.masukan_nama.atur_pesan_kesalahan("Nama pemasok wajib diisi.")
            return

        data = {
            "kode_pemasok": code,
            "nama": name,
            "nama_kontak": self.masukan_kontak.ambil_nilai() or None,
            "telepon": self.masukan_telepon.ambil_nilai() or None,
            "alamat": self.masukan_alamat.ambil_nilai() or None,
        }

        if self.saat_simpan:
            try:
                self.saat_simpan(data)
                self.destroy()
            except Exception as kesalahan:
                messagebox.showerror("Kesalahan", str(kesalahan), parent=self)


class TransactionDialog(BaseModalDialog):
    """Dialog Pencatatan Stok Masuk (IN) atau Keluar (OUT)."""

    def __init__(
        self,
        parent,
        daftar_produk: List[Dict[str, Any]],
        jenis_awal: str = "IN",
        saat_simpan: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        label_tipe = "Stok Masuk (IN)" if jenis_awal == "IN" else "Stok Keluar (OUT)"
        super().__init__(parent, f"Catat Transaksi {label_tipe}", width=480, height=480)
        self.daftar_produk = daftar_produk
        self.saat_simpan = saat_simpan

        # Mapping Produk
        self.peta_produk = {
            f"{p['sku']} - {p['nama']} (Stok: {float(p['jumlah_stok']):.0f})": p
            for p in daftar_produk
        }
        prod_options = list(self.peta_produk.keys())

        self.masukan_produk = FormField(
            self.isi_formulir,
            label="Pilih Produk *",
            jenis_masukan="combobox",
            opsi=prod_options,
            default_value=prod_options[0] if prod_options else "",
            readonly=True,
        )
        self.masukan_produk.pack(fill="x", pady=(0, 8))

        self.masukan_jenis = FormField(
            self.isi_formulir,
            label="Tipe Transaksi *",
            jenis_masukan="combobox",
            opsi=["IN (Barang Masuk / Pembelian)", "OUT (Penyesuaian Keluar)"],
            default_value="IN (Barang Masuk / Pembelian)" if jenis_awal == "IN" else "OUT (Penyesuaian Keluar)",
            readonly=True,
        )
        self.masukan_jenis.pack(fill="x", pady=(0, 8))

        self.masukan_kuantitas = FormField(
            self.isi_formulir,
            label="Jumlah Kuantitas *",
            default_value="10",
        )
        self.masukan_kuantitas.pack(fill="x", pady=(0, 8))

        self.masukan_biaya = FormField(
            self.isi_formulir,
            label="Biaya / Harga Satuan (Rp)",
            default_value="0",
        )
        self.masukan_biaya.pack(fill="x", pady=(0, 8))

        self.masukan_catatan = FormField(
            self.isi_formulir,
            label="Catatan Transaksi",
            default_value=f"Transaksi {jenis_awal}",
        )
        self.masukan_catatan.pack(fill="x", pady=(0, 8))

    def _saat_disimpan(self):
        sel_prod_str = self.masukan_produk.ambil_nilai()
        produk = self.peta_produk.get(sel_prod_str)
        if not produk:
            self.masukan_produk.atur_pesan_kesalahan("Pilih produk yang valid.")
            return

        teks_jenis = self.masukan_jenis.ambil_nilai()
        jenis_transaksi = "IN" if "IN" in teks_jenis else "OUT"

        try:
            kuantitas = float(self.masukan_kuantitas.ambil_nilai())
            if kuantitas <= 0:
                raise ValueError
        except ValueError:
            self.masukan_kuantitas.atur_pesan_kesalahan("Kuantitas harus berupa angka lebih besar dari 0.")
            return

        try:
            biaya = float(self.masukan_biaya.ambil_nilai() or 0)
            if biaya < 0:
                raise ValueError
        except ValueError:
            self.masukan_biaya.atur_pesan_kesalahan("Biaya tidak boleh bernilai negatif.")
            return

        data = {
            "id_produk": produk["id_produk"],
            "jenis_transaksi": jenis_transaksi,
            "kuantitas": kuantitas,
            "biaya_satuan": biaya,
            "id_pemasok": produk.get("id_pemasok") if jenis_transaksi == "IN" else None,
            "catatan": self.masukan_catatan.ambil_nilai(),
        }

        if self.saat_simpan:
            try:
                self.saat_simpan(data)
                self.destroy()
            except Exception as kesalahan:
                messagebox.showerror("Gagal", str(kesalahan), parent=self)


class SaleDialog(BaseModalDialog):
    """Dialog Pencatatan Penjualan Baru."""

    def __init__(
        self,
        parent,
        daftar_produk: List[Dict[str, Any]],
        saat_simpan: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__(parent, "Catat Penjualan Barang", width=480, height=440)
        self.daftar_produk = daftar_produk
        self.saat_simpan = saat_simpan

        self.peta_produk = {
            f"{p['sku']} - {p['nama']} (Tersedia: {float(p['jumlah_stok']):.0f} {p.get('satuan','pcs')})": p
            for p in daftar_produk
        }
        prod_options = list(self.peta_produk.keys())

        self.masukan_produk = FormField(
            self.isi_formulir,
            label="Pilih Produk yang Terjual *",
            jenis_masukan="combobox",
            opsi=prod_options,
            default_value=prod_options[0] if prod_options else "",
            readonly=True,
        )
        self.masukan_produk.pack(fill="x", pady=(0, 8))

        self.masukan_kuantitas = FormField(
            self.isi_formulir,
            label="Kuantitas Terjual *",
            default_value="1",
        )
        self.masukan_kuantitas.pack(fill="x", pady=(0, 8))

        self.masukan_harga = FormField(
            self.isi_formulir,
            label="Harga Jual Satuan (Rp) *",
            default_value="0",
        )
        self.masukan_harga.pack(fill="x", pady=(0, 8))

        # Auto-update harga jual ketika produk dipilih
        self.masukan_produk.kontrol.bind("<<ComboboxSelected>>", self._saat_produk_berubah)
        self._saat_produk_berubah()

        self.masukan_catatan = FormField(
            self.isi_formulir,
            label="Catatan Penjualan",
            default_value="Penjualan Pelanggan",
        )
        self.masukan_catatan.pack(fill="x", pady=(0, 8))

    def _saat_produk_berubah(self, *args):
        sel = self.masukan_produk.ambil_nilai()
        produk = self.peta_produk.get(sel)
        if produk:
            self.masukan_harga.atur_nilai(str(float(produk.get("harga_jual", 0))))

    def _saat_disimpan(self):
        produk = self.peta_produk.get(self.masukan_produk.ambil_nilai())
        if not produk:
            self.masukan_produk.atur_pesan_kesalahan("Pilih produk yang valid.")
            return

        try:
            kuantitas = float(self.masukan_kuantitas.ambil_nilai())
            if kuantitas <= 0:
                raise ValueError
        except ValueError:
            self.masukan_kuantitas.atur_pesan_kesalahan("Kuantitas harus angka > 0.")
            return

        try:
            price = float(self.masukan_harga.ambil_nilai())
            if price < 0:
                raise ValueError
        except ValueError:
            self.masukan_harga.atur_pesan_kesalahan("Harga jual tidak boleh negatif.")
            return

        data = {
            "id_produk": produk["id_produk"],
            "jumlah_terjual": kuantitas,
            "harga_satuan": price,
            "catatan": self.masukan_catatan.ambil_nilai(),
        }

        if self.saat_simpan:
            try:
                self.saat_simpan(data)
                self.destroy()
            except Exception as kesalahan:
                messagebox.showerror("Gagal", str(kesalahan), parent=self)
