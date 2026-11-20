import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple
from gui.theme import (
    BG_CARD,
    BORDER_COLOR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PRIMARY,
)


class DataTable(tk.Frame):
    """
    Komponen Tabel Data interaktif modern berbasis ttk.Treeview
    dilengkapi kotak pencarian, scrollbar, dan dukungan seleksi.
    """

    def __init__(
        self,
        parent,
        columns: List[Tuple[str, str, int, str]],  # [(col_id, header_text, width, anchor)]
        show_search: bool = True,
        search_placeholder: str = "Cari data...",
        saat_pilih: Optional[Callable[[Dict[str, Any]], None]] = None,
        saat_klik_ganda: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            **kwargs,
        )

        self.metadata_kolom = columns
        self.data_mentah: List[Dict[str, Any]] = []
        self.data_tersaring: List[Dict[str, Any]] = []
        self.saat_pilih = saat_pilih
        self.saat_klik_ganda = saat_klik_ganda

        # 1. Baris Atas: Kotak Pencarian & Ringkasan Baris
        if show_search:
            top_bar = tk.Frame(self, bg=BG_CARD, padx=12, pady=10)
            top_bar.pack(fill="x")

            lbl_search = tk.Label(
                top_bar, text="🔍", font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED
            )
            lbl_search.pack(side="left", padx=(0, 4))

            self.variabel_pencarian = tk.StringVar()
            self.variabel_pencarian.trace_add("write", self._saat_pencarian_berubah)

            self.masukan_pencarian = tk.Entry(
                top_bar,
                textvariable=self.variabel_pencarian,
                font=FONT_BODY,
                fg=TEXT_PRIMARY,
                bg="#F8FAFC",
                relief="flat",
                highlightthickness=1,
                highlightbackground=BORDER_COLOR,
                highlightcolor=ACCENT_PRIMARY,
                width=30,
            )
            self.masukan_pencarian.pack(side="left", ipady=4, padx=(0, 10))

            self.label_jumlah = tk.Label(
                top_bar,
                text="0 item",
                font=FONT_SMALL,
                fg=TEXT_MUTED,
                bg=BG_CARD,
            )
            self.label_jumlah.pack(side="right")
        else:
            self.variabel_pencarian = None

        # 2. Container Treeview & Scrollbar
        tree_container = tk.Frame(self, bg=BG_CARD)
        tree_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        col_ids = [c[0] for c in columns]
        self.tabel_pohon = ttk.Treeview(
            tree_container,
            columns=col_ids,
            show="headings",
            selectmode="browse",
        )

        # Konfigurasi Header Kolom
        for col_id, header, width, anchor in columns:
            self.tabel_pohon.heading(col_id, text=header, anchor=anchor)
            self.tabel_pohon.column(col_id, width=width, minwidth=width // 2, anchor=anchor)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tabel_pohon.yview)
        scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tabel_pohon.xview)
        self.tabel_pohon.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tabel_pohon.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Konfigurasi Tag Warna Baris Bergantian
        self.tabel_pohon.tag_configure("odd", background="#FFFFFF")
        self.tabel_pohon.tag_configure("even", background="#F8FAFC")
        self.tabel_pohon.tag_configure("status_aman", foreground="#059669")
        self.tabel_pohon.tag_configure("status_warning", foreground="#D97706")
        self.tabel_pohon.tag_configure("status_danger", foreground="#DC2626")

        # Event Bindings
        self.tabel_pohon.bind("<<TreeviewSelect>>", self._tangani_pemilihan)
        self.tabel_pohon.bind("<Double-1>", self._tangani_klik_ganda)

    def atur_data(self, data: List[Dict[str, Any]]):
        """Mengisi data ke dalam tabel dari list dictionary."""
        self.data_mentah = list(data)
        self._terapkan_penyaring()

    def _terapkan_penyaring(self):
        kueri = self.variabel_pencarian.get().strip().lower() if self.variabel_pencarian else ""

        if not kueri:
            self.data_tersaring = list(self.data_mentah)
        else:
            self.data_tersaring = [
                baris
                for baris in self.data_mentah
                if any(kueri in str(v).lower() for v in baris.values())
            ]

        # Kosongkan Treeview
        for elemen in self.tabel_pohon.get_children():
            self.tabel_pohon.delete(elemen)

        # Masukkan data tersaring
        for indeks, baris in enumerate(self.data_tersaring):
            values = [baris.get(col_id, "") for col_id, _, _, _ in self.metadata_kolom]
            tag = "even" if indeks % 2 == 0 else "odd"

            # Cek status untuk aksen warna teks
            status_val = str(baris.get("status", "")).upper()
            tags = [tag]
            if "AMAN" in status_val or "IN STOCK" in status_val:
                tags.append("status_aman")
            elif "REORDER" in status_val or "LOW" in status_val:
                tags.append("status_warning")
            elif "HABIS" in status_val or "OUT" in status_val or "KRITIS" in status_val:
                tags.append("status_danger")

            self.tabel_pohon.insert("", "end", iid=str(indeks), values=values, tags=tuple(tags))

        if hasattr(self, "lbl_count"):
            self.label_jumlah.config(text=f"{len(self.data_tersaring)} item")

    def _saat_pencarian_berubah(self, *args):
        self._terapkan_penyaring()

    def _tangani_pemilihan(self, peristiwa):
        if not self.saat_pilih:
            return
        terpilih = self.ambil_baris_terpilih()
        if terpilih:
            self.saat_pilih(terpilih)

    def _tangani_klik_ganda(self, peristiwa):
        if not self.saat_klik_ganda:
            return
        terpilih = self.ambil_baris_terpilih()
        if terpilih:
            self.saat_klik_ganda(terpilih)

    def ambil_baris_terpilih(self) -> Optional[Dict[str, Any]]:
        """Mengembalikan data dictionary baris yang sedang dipilih pengguna."""
        selection = self.tabel_pohon.selection()
        if not selection:
            return None
        indeks = int(selection[0])
        if 0 <= indeks < len(self.data_tersaring):
            return self.data_tersaring[indeks]
        return None
