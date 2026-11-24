from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from math import ceil, sqrt
from pathlib import Path

from config.settings import HARI_TAHUNAN_BAKU
from database.connection import buat_koneksi


DATA_PEMASOK = (
    ("SUP-001", "Sumber Pangan Nusantara", "Tim Penjualan", "021-555-0101", "Jakarta"),
)

DATA_PRODUK = (
    ("BRG-001", "Kopi Arabika 250 g", "Minuman", "SUP-001", "pcs", "93", "45000", "60000", "20"),
    ("BRG-002", "Teh Melati 100 g", "Minuman", "SUP-001", "pcs", "75", "18000", "25000", "15"),
)

DATA_TRANSAKSI = (
    ("SEED-IN-001", "BRG-001", "SUP-001", "IN", "100", "45000", 30, "Stok awal"),
    ("SEED-IN-002", "BRG-002", "SUP-001", "IN", "80", "18000", 30, "Stok awal"),
    ("SEED-SALE-001", "BRG-001", None, "OUT", "7", "45000", 3, "Penjualan contoh"),
    ("SEED-SALE-002", "BRG-002", None, "OUT", "5", "18000", 2, "Penjualan contoh"),
)

DATA_PENJUALAN = (
    ("SEED-SALE-001", "BRG-001", "7", "60000", 3),
    ("SEED-SALE-002", "BRG-002", "5", "25000", 2),
)

MASUKAN_ANALISIS = (
    ("BRG-001", "2400", "90000", "4500", "2"),
    ("BRG-002", "1800", "90000", "1800", "2"),
)


def _ubah_ke_desimal(nilai):
    return Decimal(str(nilai))


def _hitung_hasil_analisis(
    permintaan_tahunan,
    biaya_pemesanan,
    biaya_penyimpanan,
    waktu_tunggu_hari,
):
    kuantitas_pemesanan_ekonomis = sqrt(
        (2 * float(permintaan_tahunan) * float(biaya_pemesanan)) / float(biaya_penyimpanan)
    )
    rata_rata_permintaan_harian = (
        float(permintaan_tahunan) / HARI_TAHUNAN_BAKU
    )
    stok_pengaman = ceil(rata_rata_permintaan_harian * float(waktu_tunggu_hari))
    titik_pemesanan_ulang = (
        float(rata_rata_permintaan_harian) * float(waktu_tunggu_hari) + stok_pengaman
    )
    return (
        _ubah_ke_desimal(f"{kuantitas_pemesanan_ekonomis:.2f}"),
        _ubah_ke_desimal(f"{stok_pengaman:.2f}"),
        _ubah_ke_desimal(f"{titik_pemesanan_ulang:.2f}"),
    )


def siapkan_basis_data():
    sql_skema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    id_pemasok_berdasarkan_kode = {}
    id_produk_berdasarkan_sku = {}

    with buat_koneksi() as koneksi:
        koneksi.execute(sql_skema)

        for kode, nama, kontak, telepon, alamat in DATA_PEMASOK:
            baris = koneksi.execute(
                """
                INSERT INTO suppliers (kode_pemasok, nama, nama_kontak, telepon, alamat)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (kode_pemasok) DO UPDATE SET
                    nama = EXCLUDED.nama,
                    nama_kontak = EXCLUDED.nama_kontak,
                    telepon = EXCLUDED.telepon,
                    alamat = EXCLUDED.alamat
                RETURNING id_pemasok
                """,
                (kode, nama, kontak, telepon, alamat),
            ).fetchone()
            id_pemasok_berdasarkan_kode[kode] = baris[0]

        for (
            sku,
            nama,
            kategori,
            kode_pemasok,
            satuan,
            stok,
            biaya_satuan,
            harga_jual,
            stok_minimum,
        ) in DATA_PRODUK:
            baris = koneksi.execute(
                """
                INSERT INTO products (
                    sku, nama, kategori, id_pemasok, satuan, jumlah_stok,
                    biaya_satuan, harga_jual, stok_minimum
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO UPDATE SET
                    nama = EXCLUDED.nama,
                    kategori = EXCLUDED.kategori,
                    id_pemasok = EXCLUDED.id_pemasok,
                    satuan = EXCLUDED.satuan,
                    jumlah_stok = EXCLUDED.jumlah_stok,
                    biaya_satuan = EXCLUDED.biaya_satuan,
                    harga_jual = EXCLUDED.harga_jual,
                    stok_minimum = EXCLUDED.stok_minimum
                RETURNING id_produk
                """,
                (
                    sku,
                    nama,
                    kategori,
                    id_pemasok_berdasarkan_kode[kode_pemasok],
                    satuan,
                    _ubah_ke_desimal(stok),
                    _ubah_ke_desimal(biaya_satuan),
                    _ubah_ke_desimal(harga_jual),
                    _ubah_ke_desimal(stok_minimum),
                ),
            ).fetchone()
            id_produk_berdasarkan_sku[sku] = baris[0]

        for kode, sku, kode_pemasok, jenis, kuantitas, biaya_satuan, hari_lalu, catatan in DATA_TRANSAKSI:
            koneksi.execute(
                """
                INSERT INTO transactions (
                    kode_transaksi, id_produk, id_pemasok, jenis_transaksi,
                    kuantitas, biaya_satuan, tanggal_transaksi, catatan
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (kode_transaksi) DO UPDATE SET
                    id_produk = EXCLUDED.id_produk,
                    id_pemasok = EXCLUDED.id_pemasok,
                    jenis_transaksi = EXCLUDED.jenis_transaksi,
                    kuantitas = EXCLUDED.kuantitas,
                    biaya_satuan = EXCLUDED.biaya_satuan,
                    catatan = EXCLUDED.catatan
                """,
                (
                    kode,
                    id_produk_berdasarkan_sku[sku],
                    id_pemasok_berdasarkan_kode.get(kode_pemasok),
                    jenis,
                    _ubah_ke_desimal(kuantitas),
                    _ubah_ke_desimal(biaya_satuan),
                    datetime.now(timezone.utc) - timedelta(days=hari_lalu),
                    catatan,
                ),
            )

        for kode, sku, kuantitas, harga_satuan, hari_lalu in DATA_PENJUALAN:
            id_transaksi = koneksi.execute(
                "SELECT id_transaksi FROM transactions WHERE kode_transaksi = %s",
                (kode,),
            ).fetchone()[0]
            koneksi.execute(
                """
                INSERT INTO sales_history (
                    id_transaksi, id_produk, kuantitas_terjual, harga_satuan, tanggal_penjualan
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id_transaksi) DO UPDATE SET
                    id_produk = EXCLUDED.id_produk,
                    kuantitas_terjual = EXCLUDED.kuantitas_terjual,
                    harga_satuan = EXCLUDED.harga_satuan
                """,
                (
                    id_transaksi,
                    id_produk_berdasarkan_sku[sku],
                    _ubah_ke_desimal(kuantitas),
                    _ubah_ke_desimal(harga_satuan),
                    datetime.now(timezone.utc) - timedelta(days=hari_lalu),
                ),
            )

        for sku, *masukan_mentah in MASUKAN_ANALISIS:
            masukan = tuple(_ubah_ke_desimal(nilai) for nilai in masukan_mentah)
            kuantitas_pemesanan_ekonomis, stok_pengaman, titik_pemesanan_ulang = _hitung_hasil_analisis(*masukan)
            rata_rata_permintaan_harian = (
                masukan[0] / Decimal(str(HARI_TAHUNAN_BAKU))
            )
            koneksi.execute(
                """
                INSERT INTO inventory_analysis (
                    id_produk, tanggal_analisis, permintaan_tahunan, biaya_pemesanan,
                    biaya_penyimpanan_per_unit_tahun, rata_rata_permintaan_harian,
                    simpangan_baku_permintaan_harian, waktu_tunggu_hari, skor_z, kuantitas_pemesanan_ekonomis,
                    stok_pengaman, titik_pemesanan_ulang
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
                """,
                (
                    id_produk_berdasarkan_sku[sku],
                    date.today(),
                    *masukan[:3],
                    rata_rata_permintaan_harian,
                    Decimal("0"),
                    masukan[3],
                    Decimal("0"),
                    kuantitas_pemesanan_ekonomis,
                    stok_pengaman,
                    titik_pemesanan_ulang,
                ),
            )


if __name__ == "__main__":
    siapkan_basis_data()
    print("Skema database dan data contoh berhasil disiapkan.")