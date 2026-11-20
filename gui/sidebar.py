import tkinter as tk
from typing import Callable, Dict
from gui.theme import (
    BG_SIDEBAR,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_TITLE,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_LIGHT,
)


class Sidebar(tk.Frame):
    """
    Bilah navigasi vertikal samping (Sidebar) modern
    dengan highlight tab aktif, icon representatif, dan brand SmartStock.
    """

    DAFTAR_MENU = [
        ("dashboard", "📊  Dasbor Utama"),
        ("products", "📦  Data Produk"),
        ("suppliers", "🏭  Pemasok (Suppliers)"),
        ("transactions", "🔄  Transaksi Stok (IN/OUT)"),
        ("sales", "💰  Riwayat Penjualan"),
        ("inventory_analysis", "📈  Optimasi EOQ & ROP"),
        ("forecasting", "🔮  Peramalan Permintaan"),
        ("reports", "📑  Laporan & Valuasi"),
        ("import_export", "📂  Impor / Ekspor CSV"),
    ]

    def __init__(self, parent, saat_navigasi: Callable[[str], None], **kwargs):
        super().__init__(
            parent,
            bg=BG_SIDEBAR,
            width=230,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            **kwargs,
        )
        self.pack_propagate(False)
        self.saat_navigasi = saat_navigasi
        self.daftar_tombol: Dict[str, tk.Label] = {}
        self.halaman_aktif = "dashboard"

        # 1. Bagian Brand / Logo Atas
        brand_frame = tk.Frame(self, bg=BG_SIDEBAR, padx=18, pady=20)
        brand_frame.pack(fill="x")

        lbl_logo = tk.Label(
            brand_frame,
            text="⚡ SmartStock",
            font=FONT_TITLE,
            fg=ACCENT_PRIMARY,
            bg=BG_SIDEBAR,
            anchor="w",
        )
        lbl_logo.pack(fill="x")

        lbl_sub = tk.Label(
            brand_frame,
            text="Inventory Optimization System",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_SIDEBAR,
            anchor="w",
        )
        lbl_sub.pack(fill="x", pady=(2, 0))

        sep = tk.Frame(self, height=1, bg=BORDER_COLOR)
        sep.pack(fill="x", padx=14, pady=(0, 10))

        # 2. Tombol Navigasi Menu
        menu_container = tk.Frame(self, bg=BG_SIDEBAR, padx=10)
        menu_container.pack(fill="both", expand=True)

        for key, label in self.DAFTAR_MENU:
            btn = tk.Label(
                menu_container,
                text=f"  {label}",
                font=FONT_BODY,
                fg=TEXT_SECONDARY,
                bg=BG_SIDEBAR,
                anchor="w",
                padx=12,
                pady=9,
                cursor="hand2",
            )
            btn.pack(fill="x", pady=2)
            btn.bind("<Button-1>", lambda e, k=key: self._saat_menu_diklik(k))
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._saat_diarahkan(b, k, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._saat_diarahkan(b, k, False))
            self.daftar_tombol[key] = btn

        # 3. Footer Bawah
        footer_frame = tk.Frame(self, bg=BG_SIDEBAR, padx=14, pady=14)
        footer_frame.pack(fill="x", side="bottom")

        lbl_ver = tk.Label(
            footer_frame,
            text="SmartStock v2.0 • PostgreSQL",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_SIDEBAR,
            anchor="w",
        )
        lbl_ver.pack(fill="x")

        self.atur_menu_aktif("dashboard")

    def _saat_menu_diklik(self, page_key: str):
        self.atur_menu_aktif(page_key)
        self.saat_navigasi(page_key)

    def _saat_diarahkan(self, kontrol: tk.Label, page_key: str, is_hover: bool):
        if page_key == self.halaman_aktif:
            return
        if is_hover:
            kontrol.config(bg="#F8FAFC", fg=TEXT_PRIMARY)
        else:
            kontrol.config(bg=BG_SIDEBAR, fg=TEXT_SECONDARY)

    def atur_menu_aktif(self, page_key: str):
        self.halaman_aktif = page_key
        for key, btn in self.daftar_tombol.items():
            if key == page_key:
                btn.config(
                    bg=ACCENT_PRIMARY_LIGHT,
                    fg=ACCENT_PRIMARY,
                    font=FONT_BODY_BOLD,
                )
            else:
                btn.config(
                    bg=BG_SIDEBAR,
                    fg=TEXT_SECONDARY,
                    font=FONT_BODY,
                )
