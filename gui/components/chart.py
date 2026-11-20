import math
import tkinter as tk
from typing import Dict, List, Optional, Tuple
from gui.theme import (
    BG_CARD,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    ACCENT_DANGER,
)


class BarChart(tk.Frame):
    """
    Komponen Grafik Batang modern berbasis Tkinter Canvas
    dengan garis bantu horizontal, label sumbu X/Y, dan efek hover.
    """

    def __init__(
        self,
        parent,
        title: str = "Aktivitas Penjualan & Transaksi",
        width: int = 500,
        height: int = 240,
        warna_batang: str = ACCENT_PRIMARY,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs,
        )

        self.lebar_grafik = width
        self.tinggi_grafik = height
        self.warna_batang = warna_batang

        # Judul Grafik
        self.label_judul = tk.Label(
            self,
            text=title,
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_judul.pack(fill="x", pady=(0, 10))

        # Canvas untuk menggambar grafik
        self.kanvas = tk.Canvas(
            self,
            bg=BG_CARD,
            width=self.lebar_grafik,
            height=self.tinggi_grafik,
            highlightthickness=0,
        )
        self.kanvas.pack(fill="both", expand=True)

    def atur_data(
        self,
        categories: List[str],
        values: List[float],
        value_prefix: str = "",
        highlight_last: bool = True,
    ):
        self.kanvas.delete("all")
        if not categories or not values:
            self.kanvas.create_text(
                self.lebar_grafik // 2,
                self.tinggi_grafik // 2,
                text="Belum ada data untuk ditampilkan",
                fill=TEXT_MUTED,
                font=FONT_SMALL,
            )
            return

        w = self.kanvas.winfo_width()
        h = self.kanvas.winfo_height()
        if w < 100:
            w = self.lebar_grafik
        if h < 100:
            h = self.tinggi_grafik

        padding_left = 40
        padding_right = 20
        padding_top = 25
        padding_bottom = 30

        plot_w = w - padding_left - padding_right
        plot_h = h - padding_top - padding_bottom

        max_val = max(values) if max(values) > 0 else 1.0

        # Garis bantu horizontal (3 garis)
        for i in range(4):
            rasio_y = i / 3
            y = padding_top + (plot_h * (1 - rasio_y))
            self.kanvas.create_line(
                padding_left,
                y,
                w - padding_right,
                y,
                fill="#F1F5F9",
                width=1,
                dash=(3, 3),
            )
            val_label = f"{value_prefix}{int(max_val * rasio_y):,}"
            self.kanvas.create_text(
                padding_left - 8,
                y,
                text=val_label,
                fill=TEXT_MUTED,
                font=FONT_SMALL,
                anchor="e",
            )

        n = len(categories)
        slot_w = plot_w / n
        bar_w = min(max(slot_w * 0.55, 12), 40)

        for i, (kategori, val) in enumerate(zip(categories, values)):
            titik_tengah_x = padding_left + (i * slot_w) + (slot_w / 2)
            bar_height = (float(val) / max_val) * plot_h if max_val > 0 else 0
            y1 = padding_top + plot_h - bar_height
            y2 = padding_top + plot_h

            x1 = titik_tengah_x - (bar_w / 2)
            x2 = titik_tengah_x + (bar_w / 2)

            is_highlight = highlight_last and (i == n - 1 or i == n // 2)
            fill_c = "#818CF8" if is_highlight else self.warna_batang

            # Gambar batang (batang atas sedikit melengkung / rounded feel)
            self.kanvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=fill_c,
                outline="",
            )

            # Angka nilai di atas batang jika batang cukup tinggi
            if bar_height > 15:
                self.kanvas.create_text(
                    titik_tengah_x,
                    y1 - 8,
                    text=f"{int(val)}",
                    fill=TEXT_PRIMARY,
                    font=FONT_SMALL,
                )

            # Label sumbu X
            kategori_tampil = kategori if len(kategori) <= 8 else kategori[:7] + "…"
            self.kanvas.create_text(
                titik_tengah_x,
                h - 12,
                text=kategori_tampil,
                fill=TEXT_MUTED,
                font=FONT_SMALL,
            )


class DonutChart(tk.Frame):
    """
    Komponen Diagram Donat (Donut Chart) modern berbasis Tkinter Canvas
    lengkap dengan legenda warna, proporsi persen, dan ringkasan di tengah.
    """

    def __init__(
        self,
        parent,
        title: str = "Peringatan Stok & Inventaris",
        width: int = 340,
        height: int = 240,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs,
        )

        self.lebar_grafik = width
        self.tinggi_grafik = height

        # Judul Diagram
        self.label_judul = tk.Label(
            self,
            text=title,
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_judul.pack(fill="x", pady=(0, 6))

        # Canvas Diagram Donut
        self.kanvas = tk.Canvas(
            self,
            bg=BG_CARD,
            width=self.lebar_grafik,
            height=140,
            highlightthickness=0,
        )
        self.kanvas.pack(fill="x")

        # Container Legenda di bagian bawah
        self.wadah_legenda = tk.Frame(self, bg=BG_CARD)
        self.wadah_legenda.pack(fill="x", pady=(8, 0))

    def atur_data(self, data: Dict[str, Tuple[float, str]]):
        """
        data: {'Nama Label': (jumlah, warna_hex)}
        contoh: {
            'Aman (In Stock)': (10, ACCENT_SUCCESS),
            'Perlu Reorder': (4, ACCENT_WARNING),
            'Habis (Out of Stock)': (1, ACCENT_DANGER)
        }
        """
        self.kanvas.delete("all")
        for kontrol in self.wadah_legenda.winfo_children():
            kontrol.destroy()

        total = sum(val[0] for val in data.values())

        if total <= 0:
            self.kanvas.create_text(
                self.lebar_grafik // 2,
                70,
                text="Semua stok 0",
                fill=TEXT_MUTED,
                font=FONT_SMALL,
            )
            return

        cx = self.lebar_grafik // 2
        cy = 70
        r_outer = 56
        r_inner = 36

        start_angle = 90.0

        for label, (val, color) in data.items():
            if val <= 0:
                continue
            extent = (val / total) * 360.0

            # Gambar arc luar
            self.kanvas.create_arc(
                cx - r_outer,
                cy - r_outer,
                cx + r_outer,
                cy + r_outer,
                start=start_angle,
                extent=extent,
                fill=color,
                outline=BG_CARD,
                width=2,
            )
            start_angle += extent

        # Gambar lingkaran dalam untuk membuat lubang donat
        self.kanvas.create_oval(
            cx - r_inner,
            cy - r_inner,
            cx + r_inner,
            cy + r_inner,
            fill=BG_CARD,
            outline="",
        )

        # Angka total di pusat donat
        self.kanvas.create_text(
            cx,
            cy - 6,
            text=str(int(total)),
            fill=TEXT_PRIMARY,
            font=FONT_BODY_BOLD,
        )
        self.kanvas.create_text(
            cx,
            cy + 10,
            text="Total Unit",
            fill=TEXT_MUTED,
            font=FONT_SMALL,
        )

        # Bangun Legenda Bawah
        cols_container = tk.Frame(self.wadah_legenda, bg=BG_CARD)
        cols_container.pack(expand=True)

        for label, (val, color) in data.items():
            persentase = (val / total * 100) if total > 0 else 0
            item_frame = tk.Frame(cols_container, bg=BG_CARD, padx=8)
            item_frame.pack(side="left")

            dot = tk.Label(item_frame, text="●", fg=color, bg=BG_CARD, font=FONT_BODY)
            dot.pack(side="left")

            txt_info = f"{label}\n{int(val)} ({persentase:.0f}%)"
            lbl = tk.Label(
                item_frame,
                text=txt_info,
                font=FONT_SMALL,
                fg=TEXT_SECONDARY,
                bg=BG_CARD,
                justify="left",
            )
            lbl.pack(side="left", padx=(3, 0))
