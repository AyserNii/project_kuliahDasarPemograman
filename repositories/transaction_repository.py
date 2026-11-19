from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import buat_koneksi


class RepositoriTransaksi:
    """Repository untuk operasi tabel transactions di database PostgreSQL."""

    def __init__(self, koneksi=None):
        self._koneksi = koneksi

    def _ambil_koneksi(self):
        return self._koneksi if self._koneksi else buat_koneksi()

    def ambil_semua(self, batas: int = 100) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT t.*, p.sku, p.nama as nama_produk, s.nama as nama_pemasok
                    FROM transactions t
                    JOIN products p ON t.id_produk = p.id_produk
                    LEFT JOIN suppliers s ON t.id_pemasok = s.id_pemasok
                    ORDER BY t.tanggal_transaksi DESC
                    LIMIT %s
                    """,
                    (batas,),
                )
                return kursor.fetchall()

    def ambil_berdasarkan_produk(self, id_produk: int, batas: int = 100) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT t.*, p.sku, p.nama as nama_produk, s.nama as nama_pemasok
                    FROM transactions t
                    JOIN products p ON t.id_produk = p.id_produk
                    LEFT JOIN suppliers s ON t.id_pemasok = s.id_pemasok
                    WHERE t.id_produk = %s
                    ORDER BY t.tanggal_transaksi DESC
                    LIMIT %s
                    """,
                    (id_produk, batas),
                )
                return kursor.fetchall()

    def ambil_berdasarkan_kode(self, kode_transaksi: str) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT t.*, p.sku, p.nama as nama_produk, s.nama as nama_pemasok
                    FROM transactions t
                    JOIN products p ON t.id_produk = p.id_produk
                    LEFT JOIN suppliers s ON t.id_pemasok = s.id_pemasok
                    WHERE t.kode_transaksi = %s
                    """,
                    (kode_transaksi,),
                )
                return kursor.fetchone()

    def buat(
        self,
        kode_transaksi: str,
        id_produk: int,
        jenis_transaksi: str,
        kuantitas: float,
        biaya_satuan: float = 0,
        id_pemasok: Optional[int] = None,
        catatan: Optional[str] = None,
        tanggal_transaksi: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Mencatat transaksi dan langsung memperbarui stok produk dalam 1 database transaksi.
        """
        jenis_transaksi = jenis_transaksi.upper()
        if jenis_transaksi not in ("IN", "OUT"):
            raise ValueError("jenis_transaksi harus 'IN' atau 'OUT'")

        kuantitas_desimal = Decimal(str(kuantitas))
        if kuantitas_desimal <= 0:
            raise ValueError("Kuantitas harus lebih besar dari 0")

        biaya_desimal = Decimal(str(biaya_satuan))
        tanggal_transaksi = tanggal_transaksi or datetime.now(timezone.utc)

        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                # Cek ketersediaan stok jika tipe OUT
                kursor.execute(
                    "SELECT jumlah_stok FROM products WHERE id_produk = %s FOR UPDATE",
                    (id_produk,),
                )
                produk = kursor.fetchone()
                if not produk:
                    raise ValueError(f"Produk dengan ID {id_produk} tidak ditemukan")

                stok_saat_ini = produk["jumlah_stok"]
                if jenis_transaksi == "OUT" and stok_saat_ini < kuantitas_desimal:
                    raise ValueError(
                        f"Stok tidak mencukupi. Stok saat ini: {stok_saat_ini}, diminta: {kuantitas_desimal}"
                    )

                # Simpan transaksi
                kursor.execute(
                    """
                    INSERT INTO transactions (
                        kode_transaksi, id_produk, id_pemasok,
                        jenis_transaksi, kuantitas, biaya_satuan, tanggal_transaksi, catatan
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        kode_transaksi,
                        id_produk,
                        id_pemasok,
                        jenis_transaksi,
                        kuantitas_desimal,
                        biaya_desimal,
                        tanggal_transaksi,
                        catatan,
                    ),
                )
                transaksi = kursor.fetchone()

                # Perbarui stok produk
                selisih_stok = kuantitas_desimal if jenis_transaksi == "IN" else -kuantitas_desimal
                kursor.execute(
                    """
                    UPDATE products
                    SET jumlah_stok = jumlah_stok + %s
                    WHERE id_produk = %s
                    """,
                    (selisih_stok, id_produk),
                )

                koneksi.commit()
                return transaksi
