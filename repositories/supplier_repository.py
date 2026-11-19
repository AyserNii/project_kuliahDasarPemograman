from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import buat_koneksi


class RepositoriPemasok:
    """Repository untuk operasi tabel suppliers di database PostgreSQL."""

    def __init__(self, koneksi=None):
        self._koneksi = koneksi

    def _ambil_koneksi(self):
        return self._koneksi if self._koneksi else buat_koneksi()

    def ambil_semua(self) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT * FROM suppliers
                    ORDER BY id_pemasok ASC
                    """
                )
                return kursor.fetchall()

    def ambil_berdasarkan_id(self, id_pemasok: int) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    "SELECT * FROM suppliers WHERE id_pemasok = %s",
                    (id_pemasok,),
                )
                return kursor.fetchone()

    def ambil_berdasarkan_kode(self, kode_pemasok: str) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    "SELECT * FROM suppliers WHERE kode_pemasok = %s",
                    (kode_pemasok,),
                )
                return kursor.fetchone()

    def buat(
        self,
        kode_pemasok: str,
        nama: str,
        nama_kontak: Optional[str] = None,
        telepon: Optional[str] = None,
        alamat: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    INSERT INTO suppliers (kode_pemasok, nama, nama_kontak, telepon, alamat)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (kode_pemasok, nama, nama_kontak, telepon, alamat),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def perbarui(
        self,
        id_pemasok: int,
        nama: str,
        nama_kontak: Optional[str] = None,
        telepon: Optional[str] = None,
        alamat: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    UPDATE suppliers
                    SET nama = %s,
                        nama_kontak = %s,
                        telepon = %s,
                        alamat = %s
                    WHERE id_pemasok = %s
                    RETURNING *
                    """,
                    (nama, nama_kontak, telepon, alamat, id_pemasok),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def hapus(self, id_pemasok: int) -> bool:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor() as kursor:
                kursor.execute(
                    "DELETE FROM suppliers WHERE id_pemasok = %s",
                    (id_pemasok,),
                )
                terhapus = kursor.rowcount > 0
                koneksi.commit()
                return terhapus
