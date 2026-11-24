import unittest
from datetime import date
import math

from config.settings import HARI_TAHUNAN_BAKU

from services.inventory_service import LayananPersediaan


class RepositoriProdukPalsu:
    def ambil_berdasarkan_id(self, id_produk):
        return {
            "id_produk": id_produk,
            "nama": "Produk Contoh",
            "jumlah_stok": 20,
            "stok_minimum": 5,
            "biaya_satuan": 10,
        }

    def ambil_semua(self):
        return []


class RepositoriPenjualanPalsu:
    def ambil_permintaan_tahunan(self, id_produk):
        tahun_ini = date.today().year
        return [
            {"tahun": tahun_ini - 1, "total_kuantitas": 1000},
            {"tahun": tahun_ini, "total_kuantitas": 1500},
        ]


class RepositoriAnalisisPalsu:
    def simpan(self, **hasil_analisis):
        return hasil_analisis

    def ambil_semua_terbaru(self):
        return []


class TestLayananPersediaan(unittest.TestCase):
    def test_analisis_produk_mengembalikan_kunci_bahasa_indonesia(self):
        layanan = LayananPersediaan(
            repositori_produk=RepositoriProdukPalsu(),
            repositori_penjualan=RepositoriPenjualanPalsu(),
            repositori_analisis=RepositoriAnalisisPalsu(),
        )

        hasil = layanan.analisis_produk(
            id_produk=1,
        )

        self.assertIn("produk", hasil)
        self.assertIn("analisis", hasil)
        self.assertIn("rekomendasi", hasil)
        self.assertIn("biaya", hasil)
        self.assertIn("peramalan", hasil)
        self.assertEqual(len(hasil["proyeksi"]), 3)
        self.assertIn("kuantitas_pemesanan_ekonomis", hasil["analisis"])
        proyeksi_pertama = hasil["proyeksi"][0]
        pemakaian_harian = (
            proyeksi_pertama["permintaan_tahunan"] / HARI_TAHUNAN_BAKU
        )
        self.assertEqual(
            proyeksi_pertama["stok_pengaman"],
            math.ceil(pemakaian_harian * 2),
        )
        self.assertEqual(
            proyeksi_pertama["titik_pemesanan_ulang"],
            round(pemakaian_harian * 2 + proyeksi_pertama["stok_pengaman"], 2),
        )


if __name__ == "__main__":
    unittest.main()
