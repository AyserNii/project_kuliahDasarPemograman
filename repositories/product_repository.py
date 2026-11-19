from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import buat_koneksi


class RepositoriProduk:
    """Repository untuk operasi tabel products di database PostgreSQL."""

    def __init__(self, koneksi=None):
        self._koneksi = koneksi

    def _ambil_koneksi(self):
        return self._koneksi if self._koneksi else buat_koneksi()

    def ambil_semua(self) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT p.*, s.nama as nama_pemasok, s.kode_pemasok
                    FROM products p
                    LEFT JOIN suppliers s ON p.id_pemasok = s.id_pemasok
                    ORDER BY p.id_produk ASC
                    """
                )
                return kursor.fetchall()

    def ambil_berdasarkan_id(self, id_produk: int) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT p.*, s.nama as nama_pemasok, s.kode_pemasok
                    FROM products p
                    LEFT JOIN suppliers s ON p.id_pemasok = s.id_pemasok
                    WHERE p.id_produk = %s
                    """,
                    (id_produk,),
                )
                return kursor.fetchone()

    def ambil_berdasarkan_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT p.*, s.nama as nama_pemasok, s.kode_pemasok
                    FROM products p
                    LEFT JOIN suppliers s ON p.id_pemasok = s.id_pemasok
                    WHERE p.sku = %s
                    """,
                    (sku,),
                )
                return kursor.fetchone()

    def buat(
        self,
        sku: str,
        nama: str,
        kategori: Optional[str] = None,
        id_pemasok: Optional[int] = None,
        satuan: str = "pcs",
        jumlah_stok: float = 0,
        biaya_satuan: float = 0,
        harga_jual: float = 0,
        stok_minimum: float = 0,
    ) -> Dict[str, Any]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    INSERT INTO products (
                        sku, nama, kategori, id_pemasok, satuan,
                        jumlah_stok, biaya_satuan, harga_jual, stok_minimum
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        sku,
                        nama,
                        kategori,
                        id_pemasok,
                        satuan,
                        Decimal(str(jumlah_stok)),
                        Decimal(str(biaya_satuan)),
                        Decimal(str(harga_jual)),
                        Decimal(str(stok_minimum)),
                    ),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def perbarui(
        self,
        id_produk: int,
        nama: str,
        kategori: Optional[str] = None,
        id_pemasok: Optional[int] = None,
        satuan: str = "pcs",
        biaya_satuan: float = 0,
        harga_jual: float = 0,
        stok_minimum: float = 0,
    ) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    UPDATE products
                    SET nama = %s,
                        kategori = %s,
                        id_pemasok = %s,
                        satuan = %s,
                        biaya_satuan = %s,
                        harga_jual = %s,
                        stok_minimum = %s
                    WHERE id_produk = %s
                    RETURNING *
                    """,
                    (
                        nama,
                        kategori,
                        id_pemasok,
                        satuan,
                        Decimal(str(biaya_satuan)),
                        Decimal(str(harga_jual)),
                        Decimal(str(stok_minimum)),
                        id_produk,
                    ),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def perbarui_stok(self, id_produk: int, perubahan_kuantitas: float) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    UPDATE products
                    SET jumlah_stok = jumlah_stok + %s
                    WHERE id_produk = %s
                    RETURNING *
                    """,
                    (Decimal(str(perubahan_kuantitas)), id_produk),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def hapus(self, id_produk: int) -> bool:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor() as kursor:
                kursor.execute("DELETE FROM products WHERE id_produk = %s", (id_produk,))
                terhapus = kursor.rowcount > 0
                koneksi.commit()
                return terhapus

    def ambil_stok_menipis(self) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT p.*, s.nama as nama_pemasok, s.kode_pemasok
                    FROM products p
                    LEFT JOIN suppliers s ON p.id_pemasok = s.id_pemasok
                    WHERE p.jumlah_stok <= p.stok_minimum
                    ORDER BY p.jumlah_stok ASC
                    """
                )
                return kursor.fetchall()
