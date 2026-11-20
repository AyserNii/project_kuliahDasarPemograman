import tkinter as tk
from typing import Optional
from gui.theme import (
    BG_CARD,
    BORDER_COLOR,
    FONT_STAT_LABEL,
    FONT_STAT_VAL,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    ACCENT_PRIMARY,
)


class StatCard(tk.Frame):
    """
    Komponen kartu metrik/statistik bergaya modern dengan border tipis,
    judul metrik, nilai besar yang menonjol, dan lencana (badge) indikator.
    """

    def __init__(
        self,
        parent,
        title: str,
        value: str,
        badge_text: Optional[str] = None,
        badge_color: str = ACCENT_PRIMARY,
        badge_bg: str = "#EEF2FF",
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

        # Header baris atas: Judul dan Badge
        top_frame = tk.Frame(self, bg=BG_CARD)
        top_frame.pack(fill="x", expand=True)

        self.label_judul = tk.Label(
            top_frame,
            text=title.upper(),
            font=FONT_STAT_LABEL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_judul.pack(side="left")

        if badge_text:
            self.label_lencana = tk.Label(
                top_frame,
                text=f" {badge_text} ",
                font=FONT_SMALL,
                fg=badge_color,
                bg=badge_bg,
                padx=6,
                pady=2,
            )
            self.label_lencana.pack(side="right")
        else:
            self.label_lencana = None

        # Nilai angka utama
        self.label_nilai = tk.Label(
            self,
            text=str(value),
            font=FONT_STAT_VAL,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_nilai.pack(fill="x", pady=(8, 0))

    def perbarui_nilai(
        self,
        new_value: str,
        new_badge: Optional[str] = None,
        badge_color: Optional[str] = None,
        badge_bg: Optional[str] = None,
    ):
        self.label_nilai.config(text=str(new_value))
        if self.label_lencana and new_badge:
            self.label_lencana.config(text=f" {new_badge} ")
            if badge_color:
                self.label_lencana.config(fg=badge_color)
            if badge_bg:
                self.label_lencana.config(bg=badge_bg)
