from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from psycopg.rows import dict_row

from database.connection import buat_koneksi


class RepositoriAnalisis:
    """Repository untuk operasi tabel inventory_analysis di database PostgreSQL."""

    def __init__(self, koneksi=None):
        self._koneksi = koneksi

    def ambil_koneksi(self):
        return self._koneksi if self._koneksi else buat_koneksi()

    def simpan(
        self,
        id_produk: int,
        permintaan_tahunan: float,
        biaya_pemesanan: float,
        biaya_penyimpanan_per_unit_tahun: float,
        rata_rata_permintaan_harian: float,
        simpangan_baku_permintaan_harian: float,
        waktu_tunggu_hari: float,
        kuantitas_pemesanan_ekonomis: float,
        stok_pengaman: float,
        titik_pemesanan_ulang: float,
        tanggal_analisis: Optional[date] = None,
    ) -> Dict[str, Any]:
        tanggal_tujuan = tanggal_analisis or date.today()

        with self.ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    INSERT INTO inventory_analysis (
                        id_produk, tanggal_analisis, permintaan_tahunan, biaya_pemesanan,
                        biaya_penyimpanan_per_unit_tahun, rata_rata_permintaan_harian,
                        simpangan_baku_permintaan_harian, waktu_tunggu_hari, skor_z,
                        kuantitas_pemesanan_ekonomis, stok_pengaman, titik_pemesanan_ulang
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id_produk, tanggal_analisis) DO UPDATE SET
                        permintaan_tahunan = EXCLUDED.permintaan_tahunan,
                        biaya_pemesanan = EXCLUDED.biaya_pemesanan,
                        biaya_penyimpanan_per_unit_tahun = EXCLUDED.biaya_penyimpanan_per_unit_tahun,
                        rata_rata_permintaan_harian = EXCLUDED.rata_rata_permintaan_harian,
                        simpangan_baku_permintaan_harian = EXCLUDED.simpangan_baku_permintaan_harian,
                        waktu_tunggu_hari = EXCLUDED.waktu_tunggu_hari,
                        skor_z = EXCLUDED.skor_z,
                        kuantitas_pemesanan_ekonomis = EXCLUDED.kuantitas_pemesanan_ekonomis,
                        stok_pengaman = EXCLUDED.stok_pengaman,
                        titik_pemesanan_ulang = EXCLUDED.titik_pemesanan_ulang
                    RETURNING *
                    """,
                    (
                        id_produk,
                        tanggal_tujuan,
                        Decimal(str(round(permintaan_tahunan, 2))),
                        Decimal(str(round(biaya_pemesanan, 2))),
                        Decimal(str(round(biaya_penyimpanan_per_unit_tahun, 2))),
                        Decimal(str(round(rata_rata_permintaan_harian, 2))),
                        Decimal(str(round(simpangan_baku_permintaan_harian, 2))),
                        Decimal(str(round(waktu_tunggu_hari, 2))),
                        Decimal("0"),
                        Decimal(str(round(kuantitas_pemesanan_ekonomis, 2))),
                        Decimal(str(round(stok_pengaman, 2))),
                        Decimal(str(round(titik_pemesanan_ulang, 2))),
                    ),
                )
                hasil = kursor.fetchone()
                koneksi.commit()
                return hasil

    def ambil_terbaru_berdasarkan_produk(self, id_produk: int) -> Optional[Dict[str, Any]]:
        with self.ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT a.*, p.sku, p.nama as nama_produk, p.jumlah_stok, p.satuan
                    FROM inventory_analysis a
                    JOIN products p ON a.id_produk = p.id_produk
                    WHERE a.id_produk = %s
                    ORDER BY a.tanggal_analisis DESC
                    LIMIT 1
                    """,
                    (id_produk,),
                )
                return kursor.fetchone()

    def ambil_semua_terbaru(self) -> List[Dict[str, Any]]:
        with self.ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT DISTINCT ON (a.id_produk)
                        a.*, p.sku, p.nama as nama_produk, p.jumlah_stok, p.satuan, p.biaya_satuan
                    FROM inventory_analysis a
                    JOIN products p ON a.id_produk = p.id_produk
                    ORDER BY a.id_produk, a.tanggal_analisis DESC
                    """
                )
                return kursor.fetchall()

    def ambil_riwayat_berdasarkan_produk(self, id_produk: int, batas: int = 30) -> List[Dict[str, Any]]:
        with self.ambil_koneksi() as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(
                    """
                    SELECT a.*, p.sku, p.nama as nama_produk
                    FROM inventory_analysis a
                    JOIN products p ON a.id_produk = p.id_produk
                    WHERE a.id_produk = %s
                    ORDER BY a.tanggal_analisis DESC
                    LIMIT %s
                    """,
                    (id_produk, batas),
                )
                return kursor.fetchall()
