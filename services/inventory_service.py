from datetime import date
from typing import Any, Dict, List, Optional

from config.settings import (
    BIAYA_PEMESANAN_BAKU,
    HARI_TAHUNAN_BAKU,
    RASIO_BIAYA_PENYIMPANAN_BAKU,
    WAKTU_TUNGGU_HARI_BAKU,
)
from modules.analysis import tentukan_status_stok, buat_rekomendasi
from modules.forecasting import buat_peramalan_regresi_linear
from modules.inventory import (
    hitung_kuantitas_pemesanan_ekonomis,
    hitung_biaya_persediaan,
    hitung_titik_pemesanan_ulang,
    hitung_stok_pengaman,
)
from repositories.analysis_repository import RepositoriAnalisis
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan


class LayananPersediaan:
    """Service untuk mengatur alur proses pengelolaan dan optimasi inventory."""

    def __init__(
        self,
        repositori_produk: RepositoriProduk = None,
        repositori_penjualan: RepositoriPenjualan = None,
        repositori_analisis: RepositoriAnalisis = None,
    ):
        self.repositori_produk = repositori_produk or RepositoriProduk()
        self.repositori_penjualan = repositori_penjualan or RepositoriPenjualan()
        self.repositori_analisis = repositori_analisis or RepositoriAnalisis()

    def analisis_produk(
        self,
        id_produk: int,
        biaya_pemesanan: Optional[float] = None,
        rasio_biaya_penyimpanan: Optional[float] = None,
        waktu_tunggu_hari: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Menjalankan analisis persediaan untuk satu produk:
        1. Mengambil data produk & harga modal
        2. Meramalkan permintaan tahunan dengan regresi linear
        3. Menghitung EOQ, Safety Stock, dan Reorder Point untuk tiga tahun
        4. Menyimpan proyeksi tahun pertama ke tabel inventory_analysis
        """
        produk = self.repositori_produk.ambil_berdasarkan_id(id_produk)
        if not produk:
            raise ValueError(f"Produk dengan ID {id_produk} tidak ditemukan.")

        biaya_pemesanan = float(
            biaya_pemesanan
            if biaya_pemesanan is not None
            else BIAYA_PEMESANAN_BAKU
        )
        rasio_biaya_simpan = float(
            rasio_biaya_penyimpanan
            if rasio_biaya_penyimpanan is not None
            else RASIO_BIAYA_PENYIMPANAN_BAKU
        )
        waktu_tunggu_hari = float(
            waktu_tunggu_hari
            if waktu_tunggu_hari is not None
            else WAKTU_TUNGGU_HARI_BAKU
        )

        # Hitung holding cost per unit per tahun (berdasarkan unit_cost * h_rate)
        biaya_satuan = float(produk.get("biaya_satuan", 0))
        biaya_penyimpanan_per_unit = biaya_satuan * rasio_biaya_simpan
        if biaya_penyimpanan_per_unit <= 0:
            raise ValueError("Biaya satuan produk harus lebih besar dari 0 untuk menghitung biaya simpan.")

        riwayat_tahunan = self.repositori_penjualan.ambil_permintaan_tahunan(id_produk)
        hasil_peramalan = buat_peramalan_regresi_linear(riwayat_tahunan)
        proyeksi = []
        for ramalan in hasil_peramalan["ramalan"]:
            permintaan_tahunan = float(ramalan["permintaan_tahunan"])
            if permintaan_tahunan <= 0:
                raise ValueError(
                    f"Peramalan permintaan tahun {ramalan['tahun']} harus lebih besar dari 0."
                )
            rata_rata_permintaan_harian = permintaan_tahunan / HARI_TAHUNAN_BAKU
            kuantitas_pemesanan_ekonomis = hitung_kuantitas_pemesanan_ekonomis(
                permintaan_tahunan,
                biaya_pemesanan,
                biaya_penyimpanan_per_unit,
            )
            stok_pengaman = hitung_stok_pengaman(
                rata_rata_permintaan_harian,
                waktu_tunggu_hari,
            )
            titik_pemesanan_ulang = hitung_titik_pemesanan_ulang(
                rata_rata_permintaan_harian,
                waktu_tunggu_hari,
                stok_pengaman,
            )
            biaya = hitung_biaya_persediaan(
                permintaan_tahunan,
                kuantitas_pemesanan_ekonomis,
                biaya_pemesanan,
                biaya_penyimpanan_per_unit,
            )
            proyeksi.append(
                {
                    **ramalan,
                    "rata_rata_permintaan_harian": round(
                        rata_rata_permintaan_harian, 2
                    ),
                    "kuantitas_pemesanan_ekonomis": kuantitas_pemesanan_ekonomis,
                    "stok_pengaman": stok_pengaman,
                    "titik_pemesanan_ulang": titik_pemesanan_ulang,
                    **biaya,
                }
            )

        proyeksi_pertama = proyeksi[0]

        # Simpan ke database
        baris_tersimpan = self.repositori_analisis.simpan(
            id_produk=id_produk,
            permintaan_tahunan=proyeksi_pertama["permintaan_tahunan"],
            biaya_pemesanan=biaya_pemesanan,
            biaya_penyimpanan_per_unit_tahun=biaya_penyimpanan_per_unit,
            rata_rata_permintaan_harian=proyeksi_pertama[
                "rata_rata_permintaan_harian"
            ],
            simpangan_baku_permintaan_harian=0.0,
            waktu_tunggu_hari=waktu_tunggu_hari,
            kuantitas_pemesanan_ekonomis=proyeksi_pertama[
                "kuantitas_pemesanan_ekonomis"
            ],
            stok_pengaman=proyeksi_pertama["stok_pengaman"],
            titik_pemesanan_ulang=proyeksi_pertama["titik_pemesanan_ulang"],
            tanggal_analisis=date.today(),
        )

        # Rekomendasi
        stok_saat_ini = float(produk.get("jumlah_stok", 0))
        rekomendasi = buat_rekomendasi(
            nama_produk=produk["nama"],
            stok_saat_ini=stok_saat_ini,
            titik_pemesanan_ulang=proyeksi_pertama["titik_pemesanan_ulang"],
            stok_pengaman=proyeksi_pertama["stok_pengaman"],
            kuantitas_pemesanan_ekonomis=proyeksi_pertama[
                "kuantitas_pemesanan_ekonomis"
            ],
        )

        return {
            "produk": produk,
            "analisis": baris_tersimpan,
            "rekomendasi": rekomendasi,
            "biaya": proyeksi_pertama,
            "peramalan": hasil_peramalan,
            "proyeksi": proyeksi,
        }

    def analisis_semua_produk(self) -> List[Dict[str, Any]]:
        """Menjalankan analisis untuk seluruh produk yang terdaftar."""
        daftar_produk = self.repositori_produk.ambil_semua()
        daftar_hasil = []
        for produk in daftar_produk:
            try:
                hasil = self.analisis_produk(produk["id_produk"])
                daftar_hasil.append(hasil)
            except Exception as kesalahan:
                daftar_hasil.append({"produk": produk, "kesalahan": str(kesalahan)})
        return daftar_hasil

    def ambil_data_ringkasan_persediaan(self) -> Dict[str, Any]:
        """Mengumpulkan data metrik status persediaan seluruh produk."""
        daftar_produk = self.repositori_produk.ambil_semua()
        daftar_analisis = {entri["id_produk"]: entri for entri in self.repositori_analisis.ambil_semua_terbaru()}

        baris_ringkasan = []
        total_nilai_aset = 0.0

        for produk in daftar_produk:
            id_produk = produk["id_produk"]
            stok_saat_ini = float(produk.get("jumlah_stok", 0))
            biaya = float(produk.get("biaya_satuan", 0))
            total_nilai_aset += stok_saat_ini * biaya

            analisis = daftar_analisis.get(id_produk)
            if analisis:
                titik_pemesanan_ulang = float(analisis["titik_pemesanan_ulang"])
                stok_pengaman = float(analisis["stok_pengaman"])
                kuantitas_pemesanan_ekonomis = float(analisis["kuantitas_pemesanan_ekonomis"])
            else:
                titik_pemesanan_ulang = float(produk.get("stok_minimum", 0))
                stok_pengaman = 0.0
                kuantitas_pemesanan_ekonomis = 0.0

            status = tentukan_status_stok(stok_saat_ini, titik_pemesanan_ulang, stok_pengaman)
            baris_ringkasan.append({
                "id_produk": id_produk,
                "sku": produk["sku"],
                "nama": produk["nama"],
                "kategori": produk.get("kategori") or "-",
                "satuan": produk.get("satuan", "pcs"),
                "jumlah_stok": stok_saat_ini,
                "titik_pemesanan_ulang": titik_pemesanan_ulang,
                "stok_pengaman": stok_pengaman,
                "kuantitas_pemesanan_ekonomis": kuantitas_pemesanan_ekonomis,
                "status": status,
            })

        return {
            "jumlah_produk": len(daftar_produk),
            "total_nilai_aset": total_nilai_aset,
            "daftar_item": baris_ringkasan,
        }
