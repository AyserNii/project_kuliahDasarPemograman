from datetime import datetime
import tkinter as tk
from typing import Callable, Optional
from gui.theme import (
    BG_CARD,
    BORDER_COLOR,
    FONT_BODY,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
)


class Header(tk.Frame):
    """
    Bilah atas (Header) halaman aplikasi.
    Menampilkan judul halaman, deskripsi singkat, tanggal real-time,
    dan tombol aksi cepat (Refresh).
    """

    def __init__(
        self,
        parent,
        title: str = "Dasbor Inventaris",
        subtitle: str = "Pantau kondisi persediaan barang dan kesehatan stok UMKM",
        saat_muat_ulang: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=BG_CARD,
            height=70,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=24,
            pady=14,
            **kwargs,
        )
        self.pack_propagate(False)
        self.saat_muat_ulang = saat_muat_ulang

        # Sisi Kiri: Judul dan Deskripsi
        left_box = tk.Frame(self, bg=BG_CARD)
        left_box.pack(side="left", fill="y")

        self.label_judul = tk.Label(
            left_box,
            text=title,
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_judul.pack(anchor="w")

        self.label_subjudul = tk.Label(
            left_box,
            text=subtitle,
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_subjudul.pack(anchor="w")

        # Sisi Kanan: Tanggal Hari Ini & Tombol Muat Ulang
        right_box = tk.Frame(self, bg=BG_CARD)
        right_box.pack(side="right", fill="y")

        today_str = datetime.now().strftime("%d %B %Y")
        lbl_date = tk.Label(
            right_box,
            text=f"📅 {today_str}",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
        )
        lbl_date.pack(side="left", padx=(0, 16))

        if saat_muat_ulang:
            self.tombol_muat_ulang = tk.Button(
                right_box,
                text="⟳ Muat Ulang",
                font=FONT_SMALL,
                fg=ACCENT_PRIMARY,
                bg="#EEF2FF",
                activebackground="#E0E7FF",
                relief="flat",
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=saat_muat_ulang,
            )
            self.tombol_muat_ulang.pack(side="right")
        else:
            self.tombol_muat_ulang = None

    def perbarui_header(self, title: str, subtitle: str = ""):
        self.label_judul.config(text=title)
        self.label_subjudul.config(text=subtitle)
