import unittest

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
    def ambil_penjualan_harian(self, id_produk, hari):
        return []


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
            permintaan_tahunan_manual=120,
        )

        self.assertIn("produk", hasil)
        self.assertIn("analisis", hasil)
        self.assertIn("rekomendasi", hasil)
        self.assertIn("biaya", hasil)
        self.assertIn("kuantitas_pemesanan_ekonomis", hasil["analisis"])


if __name__ == "__main__":
    unittest.main()
