import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional
from gui.theme import (
    BG_CARD,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    ACCENT_PRIMARY,
    ACCENT_DANGER,
)


class FormField(tk.Frame):
    """
    Komponen field input formulir dengan label terintegrasi,
    desain border fokus, dan teks pesan error validasi.
    """

    def __init__(
        self,
        parent,
        label: str,
        jenis_masukan: str = "text",  # "text", "number", "combobox", "textarea"
        opsi: Optional[List[str]] = None,
        default_value: Any = "",
        placeholder: str = "",
        readonly: bool = False,
        **kwargs,
    ):
        super().__init__(parent, bg=BG_CARD, **kwargs)
        self.jenis_masukan = jenis_masukan

        # Label atas
        lbl = tk.Label(
            self,
            text=label,
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            anchor="w",
        )
        lbl.pack(fill="x", pady=(0, 4))

        # Kontrol input sesuai tipe
        if jenis_masukan == "combobox":
            self.variabel = tk.StringVar(value=str(default_value))
            self.kontrol = ttk.Combobox(
                self,
                textvariable=self.variabel,
                values=opsi or [],
                state="readonly" if readonly else "normal",
                font=FONT_BODY,
            )
            self.kontrol.pack(fill="x", ipady=3)
        elif jenis_masukan == "textarea":
            self.variabel = None
            self.kontrol = tk.Text(
                self,
                height=3,
                font=FONT_BODY,
                fg=TEXT_PRIMARY,
                bg="#F8FAFC",
                relief="flat",
                highlightthickness=1,
                highlightbackground=BORDER_COLOR,
                highlightcolor=ACCENT_PRIMARY,
            )
            self.kontrol.pack(fill="x")
            if default_value:
                self.kontrol.insert("1.0", str(default_value))
        else:
            self.variabel = tk.StringVar(value=str(default_value))
            self.kontrol = tk.Entry(
                self,
                textvariable=self.variabel,
                font=FONT_BODY,
                fg=TEXT_PRIMARY,
                bg="#F8FAFC",
                relief="flat",
                highlightthickness=1,
                highlightbackground=BORDER_COLOR,
                highlightcolor=ACCENT_PRIMARY,
                state="readonly" if readonly else "normal",
            )
            self.kontrol.pack(fill="x", ipady=4)

        # Label error di bawah field
        self.label_kesalahan = tk.Label(
            self,
            text="",
            font=FONT_SMALL,
            fg=ACCENT_DANGER,
            bg=BG_CARD,
            anchor="w",
        )
        self.label_kesalahan.pack(fill="x", pady=(2, 0))

    def ambil_nilai(self) -> str:
        if self.jenis_masukan == "textarea":
            return self.kontrol.get("1.0", "end-1c").strip()
        return self.variabel.get().strip()

    def atur_nilai(self, value: Any):
        if self.jenis_masukan == "textarea":
            self.kontrol.delete("1.0", "end")
            self.kontrol.insert("1.0", str(value or ""))
        else:
            self.variabel.set(str(value or ""))
        self.hapus_pesan_kesalahan()

    def atur_pesan_kesalahan(self, message: str):
        self.label_kesalahan.config(text=message)

    def hapus_pesan_kesalahan(self):
        self.label_kesalahan.config(text="")
