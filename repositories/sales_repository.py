from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from psycopg.rows import dict_row

from database.connection import buat_koneksi


class RepositoriPenjualan:
    """Repository untuk operasi tabel sales_history di database PostgreSQL."""

    def __init__(self, koneksi=None):
        self._koneksi = koneksi

    def _ambil_koneksi(self):
        return self._koneksi if self._koneksi else buat_koneksi()

    def ambil_semua(self, batas: int = 100) -> List[Dict[str, Any]]:
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT s.*, p.sku, p.nama as nama_produk, t.kode_transaksi
                    FROM sales_history s
                    JOIN products p ON s.id_produk = p.id_produk
                    JOIN transactions t ON s.id_transaksi = t.id_transaksi
                    ORDER BY s.tanggal_penjualan DESC
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
                    SELECT s.*, p.sku, p.nama as nama_produk, t.kode_transaksi
                    FROM sales_history s
                    JOIN products p ON s.id_produk = p.id_produk
                    JOIN transactions t ON s.id_transaksi = t.id_transaksi
                    WHERE s.id_produk = %s
                    ORDER BY s.tanggal_penjualan DESC
                    LIMIT %s
                    """,
                    (id_produk, batas),
                )
                return kursor.fetchall()

    def catat_penjualan(
        self,
        id_produk: int,
        kuantitas_terjual: float,
        harga_satuan: float,
        kode_transaksi: Optional[str] = None,
        tanggal_penjualan: Optional[datetime] = None,
        catatan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mencatat penjualan: membuat transaksi OUT, memperbarui stok produk,
        dan menyimpan baris ke sales_history.
        """
        kuantitas = Decimal(str(kuantitas_terjual))
        if kuantitas <= 0:
            raise ValueError("Kuantitas penjualan harus lebih besar dari 0")

        harga = Decimal(str(harga_satuan))
        if harga < 0:
            raise ValueError("Harga satuan tidak boleh negatif")

        waktu = tanggal_penjualan or datetime.now(timezone.utc)
        kode = kode_transaksi or f"SALE-{uuid.uuid4().hex[:8].upper()}"

        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                # Cek stok saat ini
                kursor.execute(
                    "SELECT jumlah_stok, biaya_satuan FROM products WHERE id_produk = %s FOR UPDATE",
                    (id_produk,),
                )
                produk = kursor.fetchone()
                if not produk:
                    raise ValueError(f"Produk dengan ID {id_produk} tidak ditemukan")

                if produk["jumlah_stok"] < kuantitas:
                    raise ValueError(
                        f"Stok tidak mencukupi untuk penjualan. Stok: {produk['jumlah_stok']}, diminta: {kuantitas}"
                    )

                biaya_satuan = produk["biaya_satuan"]

                # 1. Masukkan ke transactions (OUT)
                kursor.execute(
                    """
                    INSERT INTO transactions (
                        kode_transaksi, id_produk, id_pemasok,
                        jenis_transaksi, kuantitas, biaya_satuan, tanggal_transaksi, catatan
                    )
                    VALUES (%s, %s, NULL, 'OUT', %s, %s, %s, %s)
                    RETURNING id_transaksi
                    """,
                    (kode, id_produk, kuantitas, biaya_satuan, waktu, catatan or "Penjualan Barang"),
                )
                id_transaksi = kursor.fetchone()["id_transaksi"]

                # 2. Kurangi stok produk
                kursor.execute(
                    """
                    UPDATE products
                    SET jumlah_stok = jumlah_stok - %s
                    WHERE id_produk = %s
                    """,
                    (kuantitas, id_produk),
                )

                # 3. Masukkan ke sales_history
                kursor.execute(
                    """
                    INSERT INTO sales_history (
                        id_transaksi, id_produk, kuantitas_terjual, harga_satuan, tanggal_penjualan, catatan
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (id_transaksi, id_produk, kuantitas, harga, waktu, catatan),
                )
                catatan_penjualan = kursor.fetchone()

                koneksi.commit()
                return catatan_penjualan

    def ambil_penjualan_harian(self, id_produk: int, hari: int = 90) -> List[Dict[str, Any]]:
        """Mengambil rekap penjualan harian produk untuk analisis peramalan."""
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT DATE(tanggal_penjualan) as hari_penjualan,
                           SUM(kuantitas_terjual) as total_kuantitas,
                           SUM(kuantitas_terjual * harga_satuan) as total_pendapatan,
                           COUNT(*) as jumlah_transaksi
                    FROM sales_history
                    WHERE id_produk = %s
                      AND tanggal_penjualan >= CURRENT_DATE - (%s || ' days')::INTERVAL
                    GROUP BY DATE(tanggal_penjualan)
                    ORDER BY hari_penjualan ASC
                    """,
                    (id_produk, hari),
                )
                return kursor.fetchall()

    def ambil_permintaan_tahunan(self, id_produk: int) -> List[Dict[str, Any]]:
        """Mengambil total permintaan tahunan untuk model regresi tren."""
        with self._ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT EXTRACT(YEAR FROM tanggal_penjualan)::integer AS tahun,
                           SUM(kuantitas_terjual) AS total_kuantitas
                    FROM sales_history
                    WHERE id_produk = %s
                      AND tanggal_penjualan < DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '1 year'
                    GROUP BY EXTRACT(YEAR FROM tanggal_penjualan)
                    ORDER BY tahun ASC
                    """,
                    (id_produk,),
                )
                return kursor.fetchall()
