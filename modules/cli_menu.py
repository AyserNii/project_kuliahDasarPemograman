from datetime import datetime

from config.settings import DIREKTORI_IMPOR
from modules.analysis import tentukan_status_stok
from psycopg.errors import ForeignKeyViolation
from modules.forecasting import hitung_statistik_permintaan, pemulusan_eksponensial, rata_rata_bergerak
from modules.report import (
    grafik_batang_ascii,
    format_tabel,
    buat_laporan_ringkasan_persediaan,
    buat_grafik_stok,
    simpan_laporan_teks,
)
from modules.validation import (
    validasi_teks_tidak_kosong,
    validasi_sku,
)
from repositories.analysis_repository import RepositoriAnalisis
from repositories.product_repository import RepositoriProduk
from repositories.sales_repository import RepositoriPenjualan
from repositories.supplier_repository import RepositoriPemasok
from repositories.transaction_repository import RepositoriTransaksi
from services.export_service import LayananEkspor
from services.import_service import LayananImpor
from services.inventory_service import LayananPersediaan


def cetak_judul(judul: str):
    print("\n" + "=" * 60)
    print(f"  {judul.center(56)}")
    print("=" * 60)


def minta_teks(perintah: str, nilai_default: str = "") -> str:
    nilai = input(f"{perintah} [{nilai_default}]: " if nilai_default else f"{perintah}: ").strip()
    return nilai if nilai else nilai_default


def minta_angka(perintah: str, nilai_default: float = 0.0, izinkan_nol: bool = True) -> float:
    while True:
        masukan_mentah = input(f"{perintah} [{nilai_default}]: ").strip()
        if not masukan_mentah:
            return float(nilai_default)
        try:
            nilai = float(masukan_mentah)
            if not izinkan_nol and nilai <= 0:
                print("Nilai harus lebih besar dari 0.")
                continue
            if nilai < 0:
                print("Nilai tidak boleh negatif.")
                continue
            return nilai
        except ValueError:
            print("Masukkan angka yang valid.")


class AntarmukaSmartStockCLI:
    def __init__(self):
        self.repositori_produk = RepositoriProduk()
        self.repositori_pemasok = RepositoriPemasok()
        self.repositori_transaksi = RepositoriTransaksi()
        self.repositori_penjualan = RepositoriPenjualan()
        self.repositori_analisis = RepositoriAnalisis()

        self.layanan_impor = LayananImpor(self.repositori_produk, self.repositori_pemasok)
        self.layanan_ekspor = LayananEkspor(
            self.repositori_produk,
            self.repositori_transaksi,
            self.repositori_penjualan,
            self.repositori_analisis,
        )
        self.layanan_persediaan = LayananPersediaan(
            self.repositori_produk,
            self.repositori_penjualan,
            self.repositori_analisis,
        )

    def jalankan(self):
        while True:
            print("\n" + "=" * 60)
            print("         SMARTSTOCK CLI - SISTEM MANAJEMEN INVENTARIS")
            print("=" * 60)
            print("1. Kelola Produk (Tambah / Lihat / Edit / Hapus)")
            print("2. Kelola Supplier (Tambah / Lihat)")
            print("3. Transaksi Persediaan (Stok Masuk / Stok Keluar)")
            print("4. Riwayat Penjualan (Catat Penjualan / Lihat Riwayat)")
            print("5. Analisis Persediaan (Hitung EOQ, SS & Reorder Point)")
            print("6. Peramalan Permintaan (Demand Forecasting)")
            print("7. Laporan & Visualisasi Grafik")
            print("8. Import & Export Data CSV")
            print("0. Keluar")
            print("-" * 60)

            pilihan = input("Pilih menu [0-8]: ").strip()

            if pilihan == "0":
                print("\nTerima kasih telah menggunakan SmartStock CLI.")
                break
            elif pilihan == "1":
                self.menu_produk()
            elif pilihan == "2":
                self.menu_pemasok()
            elif pilihan == "3":
                self.menu_transaksi()
            elif pilihan == "4":
                self.menu_penjualan()
            elif pilihan == "5":
                self.menu_analisis()
            elif pilihan == "6":
                self.menu_peramalan()
            elif pilihan == "7":
                self.menu_laporan()
            elif pilihan == "8":
                self.menu_impor_ekspor()
            else:
                print("Pilihan tidak valid. Silakan pilih 0-8.")

    # ==================== 1. PRODUK ====================
    def menu_produk(self):
        while True:
            cetak_judul("MANAJEMEN DATA PRODUK")
            print("1. Lihat Semua Produk")
            print("2. Tambah Produk Baru")
            print("3. Perbarui Data Produk")
            print("4. Hapus Produk")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.tampilkan_produk()
            elif pilihan == "2":
                self.tambah_produk()
            elif pilihan == "3":
                self.perbarui_produk()
            elif pilihan == "4":
                self.hapus_produk()

    def tampilkan_produk(self):
        daftar_produk = self.repositori_produk.ambil_semua()
        if not daftar_produk:
            print("\nBelum ada produk yang terdaftar di database.")
            return

        judul_kolom = ["ID", "SKU", "Nama Produk", "Kategori", "Stok", "Satuan", "Harga Modal", "Harga Jual", "Min. Stok"]
        baris_data = []
        for produk in daftar_produk:
            baris_data.append([
                produk["id_produk"],
                produk["sku"],
                produk["nama"][:22],
                produk.get("kategori") or "-",
                f"{float(produk['jumlah_stok']):.2f}",
                produk.get("satuan", "pcs"),
                f"Rp {float(produk['biaya_satuan']):,.0f}",
                f"Rp {float(produk['harga_jual']):,.0f}",
                f"{float(produk['stok_minimum']):.2f}",
            ])
        print("\n" + format_tabel(judul_kolom, baris_data))

    def tambah_produk(self):
        cetak_judul("TAMBAH PRODUK BARU")
        try:
            sku = validasi_sku(input("Masukkan SKU (contoh: BRG-003): "))
            if self.repositori_produk.ambil_berdasarkan_sku(sku):
                print(f"[Error] Produk dengan SKU '{sku}' sudah ada.")
                return

            nama = validasi_teks_tidak_kosong(input("Nama Produk: "), "Nama Produk")
            kategori = minta_teks("Kategori (opsional)")
            satuan = minta_teks("Satuan", "pcs")

            # Tampilkan supplier yang tersedia
            daftar_pemasok = self.repositori_pemasok.ambil_semua()
            id_pemasok = None
            if daftar_pemasok:
                print("\nDaftar Supplier:")
                for elemen in daftar_pemasok:
                    print(f"  [{elemen['id_pemasok']}] {elemen['kode_pemasok']} - {elemen['nama']}")
                masukan_pemasok = input("Pilih ID Supplier (kosongkan jika tanpa pemasok): ").strip()
                if masukan_pemasok.isdigit():
                    id_pemasok = int(masukan_pemasok)

            stok_awal = minta_angka("Stok Awal", 0.0)
            biaya_satuan = minta_angka("Harga Modal/Beli per Unit (Rp)", 0.0)
            harga_jual = minta_angka("Harga Jual per Unit (Rp)", 0.0)
            stok_minimum = minta_angka("Batas Minimum Stok", 5.0)

            produk = self.repositori_produk.buat(
                sku=sku,
                nama=nama,
                kategori=kategori or None,
                id_pemasok=id_pemasok,
                satuan=satuan,
                jumlah_stok=stok_awal,
                biaya_satuan=biaya_satuan,
                harga_jual=harga_jual,
                stok_minimum=stok_minimum,
            )
            print(f"\n[SUKSES] Produk '{produk['nama']}' (SKU: {produk['sku']}) berhasil disimpan ke database!")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    def perbarui_produk(self):
        cetak_judul("PERBARUI DATA PRODUK")
        self.tampilkan_produk()
        teks_id_produk = input("\nMasukkan ID Produk yang ingin diubah: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        print(f"\nMengedit Produk: {produk['nama']} (SKU: {produk['sku']})")
        nama = minta_teks("Nama Produk", produk["nama"])
        kategori = minta_teks("Kategori", produk.get("kategori") or "")
        satuan = minta_teks("Satuan", produk.get("satuan") or "pcs")
        biaya_satuan = minta_angka("Harga Modal per Unit", float(produk["biaya_satuan"]))
        harga_jual = minta_angka("Harga Jual per Unit", float(produk["harga_jual"]))
        stok_minimum = minta_angka("Batas Minimum Stok", float(produk["stok_minimum"]))

        try:
            self.repositori_produk.perbarui(
                id_produk=produk["id_produk"],
                nama=nama,
                kategori=kategori or None,
                id_pemasok=produk.get("id_pemasok"),
                satuan=satuan,
                biaya_satuan=biaya_satuan,
                harga_jual=harga_jual,
                stok_minimum=stok_minimum,
            )
            print("\n[SUKSES] Data produk berhasil diperbarui.")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    def hapus_produk(self):
        cetak_judul("HAPUS PRODUK")
        teks_id_produk = input("Masukkan ID Produk yang ingin dihapus: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        konfirmasi = input(f"Yakin ingin menghapus produk '{produk['nama']}'? (y/n): ").strip().lower()
        if konfirmasi == "y":
            try:
                berhasil = self.repositori_produk.hapus(int(teks_id_produk))
                if berhasil:
                    print("\n[SUKSES] Produk berhasil dihapus.")
                else:
                    print("\n[Gagal] Produk tidak dapat dihapus.")
            except ForeignKeyViolation:
                print(
                    "\n[Gagal] Produk masih digunakan dalam transaksi atau analisis inventaris. "
                    "Riwayat terkait harus tetap dipertahankan, jadi produk tidak dihapus."
                )
            except Exception as kesalahan:
                print(f"\n[Gagal] Tidak dapat menghapus produk: {kesalahan}")

    # ==================== 2. SUPPLIER ====================
    def menu_pemasok(self):
        while True:
            cetak_judul("MANAJEMEN DATA SUPPLIER")
            print("1. Lihat Semua Supplier")
            print("2. Tambah Supplier Baru")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.tampilkan_pemasok()
            elif pilihan == "2":
                self.tambah_pemasok()

    def tampilkan_pemasok(self):
        daftar_pemasok = self.repositori_pemasok.ambil_semua()
        if not daftar_pemasok:
            print("\nBelum ada data pemasok di database.")
            return

        judul_kolom = ["ID", "Kode Supplier", "Nama Supplier", "Kontak Person", "No. Telepon", "Alamat"]
        baris_data = [
            [
                elemen["id_pemasok"],
                elemen["kode_pemasok"],
                elemen["nama"],
                elemen.get("nama_kontak") or "-",
                elemen.get("telepon") or "-",
                (elemen.get("alamat") or "-")[:25],
            ]
            for elemen in daftar_pemasok
        ]
        print("\n" + format_tabel(judul_kolom, baris_data))

    def tambah_pemasok(self):
        cetak_judul("TAMBAH SUPPLIER BARU")
        try:
            kode = validasi_teks_tidak_kosong(input("Kode Supplier (contoh: SUP-002): "), "Kode").upper()
            if self.repositori_pemasok.ambil_berdasarkan_kode(kode):
                print(f"[Error] Supplier dengan kode '{kode}' sudah ada.")
                return

            nama = validasi_teks_tidak_kosong(input("Nama Perusahaan/Pemasok: "), "Nama Supplier")
            kontak = minta_teks("Nama Kontak")
            telepon = minta_teks("Nomor Telepon")
            alamat = minta_teks("Alamat")

            pemasok = self.repositori_pemasok.buat(
                kode_pemasok=kode,
                nama=nama,
                nama_kontak=kontak or None,
                telepon=telepon or None,
                alamat=alamat or None,
            )
            print(f"\n[SUKSES] Supplier '{pemasok['nama']}' berhasil disimpan ke database!")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    # ==================== 3. TRANSAKSI ====================
    def menu_transaksi(self):
        while True:
            cetak_judul("MANAJEMEN TRANSAKSI PERSEDIAAN")
            print("1. Lihat Riwayat Transaksi")
            print("2. Catat Stok Masuk (IN)")
            print("3. Catat Stok Keluar / Penyesuaian (OUT)")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.tampilkan_transaksi()
            elif pilihan == "2":
                self.catat_pergerakan_persediaan("IN")
            elif pilihan == "3":
                self.catat_pergerakan_persediaan("OUT")

    def tampilkan_transaksi(self):
        daftar_transaksi = self.repositori_transaksi.ambil_semua(batas=50)
        if not daftar_transaksi:
            print("\nBelum ada riwayat transaksi.")
            return

        judul_kolom = ["Kode Transaksi", "Waktu", "SKU", "Nama Produk", "Tipe", "Jumlah", "Biaya Satuan", "Catatan"]
        baris_data = []
        for transaksi in daftar_transaksi:
            teks_waktu = transaksi["tanggal_transaksi"].strftime("%Y-%m-%d %H:%M") if transaksi.get("tanggal_transaksi") else "-"
            baris_data.append([
                transaksi["kode_transaksi"],
                teks_waktu,
                transaksi["sku"],
                transaksi["nama_produk"][:20],
                transaksi["jenis_transaksi"],
                f"{float(transaksi['kuantitas']):.2f}",
                f"Rp {float(transaksi['biaya_satuan']):,.0f}",
                (transaksi.get("catatan") or "-")[:20],
            ])
        print("\n" + format_tabel(judul_kolom, baris_data))

    def catat_pergerakan_persediaan(self, jenis_pergerakan: str):
        label = "STOK MASUK (IN)" if jenis_pergerakan == "IN" else "STOK KELUAR (OUT)"
        cetak_judul(f"CATAT {label}")

        self.tampilkan_produk()
        teks_id_produk = input("\nMasukkan ID Produk: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        kuantitas = minta_angka(f"Jumlah Kuantitas {jenis_pergerakan}", 1.0, izinkan_nol=False)
        biaya_satuan = minta_angka("Biaya per satuan (Rp)", float(produk["biaya_satuan"]))
        catatan = minta_teks("Catatan Transaksi", f"Transaksi {jenis_pergerakan}")

        # Kode transaksi unik
        kode_cap_waktu = datetime.now().strftime("%Y%m%d%H%M%S")
        kode_transaksi = f"TXN-{jenis_pergerakan}-{kode_cap_waktu}"

        try:
            transaksi = self.repositori_transaksi.buat(
                kode_transaksi=kode_transaksi,
                id_produk=produk["id_produk"],
                jenis_transaksi=jenis_pergerakan,
                kuantitas=kuantitas,
                biaya_satuan=biaya_satuan,
                id_pemasok=produk.get("id_pemasok") if jenis_pergerakan == "IN" else None,
                catatan=catatan,
            )
            produk_diperbarui = self.repositori_produk.ambil_berdasarkan_id(produk["id_produk"])
            print(f"\n[SUKSES] Transaksi {transaksi['kode_transaksi']} berhasil dicatat!")
            print(f"Stok terbaru untuk '{produk_diperbarui['nama']}': {float(produk_diperbarui['jumlah_stok']):.2f} {produk_diperbarui.get('satuan', 'pcs')}")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    # ==================== 4. PENJUALAN ====================
    def menu_penjualan(self):
        while True:
            cetak_judul("MANAJEMEN RIWAYAT PENJUALAN")
            print("1. Lihat Riwayat Penjualan")
            print("2. Catat Penjualan Baru")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.tampilkan_penjualan()
            elif pilihan == "2":
                self.catat_penjualan_baru()

    def tampilkan_penjualan(self):
        daftar_penjualan = self.repositori_penjualan.ambil_semua(batas=50)
        if not daftar_penjualan:
            print("\nBelum ada riwayat penjualan di database.")
            return

        judul_kolom = ["ID Sales", "Kode Transaksi", "Waktu Penjualan", "SKU", "Produk", "Qty Terjual", "Harga Jual", "Total"]
        baris_data = []
        for elemen in daftar_penjualan:
            kuantitas = float(elemen["kuantitas_terjual"])
            harga = float(elemen["harga_satuan"])
            teks_waktu = elemen["tanggal_penjualan"].strftime("%Y-%m-%d %H:%M") if elemen.get("tanggal_penjualan") else "-"
            baris_data.append([
                elemen["id_penjualan"],
                elemen["kode_transaksi"],
                teks_waktu,
                elemen["sku"],
                elemen["nama_produk"][:20],
                f"{kuantitas:.2f}",
                f"Rp {harga:,.0f}",
                f"Rp {kuantitas * harga:,.0f}",
            ])
        print("\n" + format_tabel(judul_kolom, baris_data))

    def catat_penjualan_baru(self):
        cetak_judul("CATAT PENJUALAN BARU")
        self.tampilkan_produk()
        teks_id_produk = input("\nMasukkan ID Produk yang Terjual: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        stok_saat_ini = float(produk["jumlah_stok"])
        print(f"Produk: {produk['nama']} | Stok Tersedia: {stok_saat_ini:.2f} {produk.get('satuan', 'pcs')}")

        kuantitas = minta_angka("Kuantitas Terjual", 1.0, izinkan_nol=False)
        harga_jual = minta_angka("Harga Jual per Unit (Rp)", float(produk["harga_jual"]))
        catatan = minta_teks("Catatan Penjualan (opsional)", "Penjualan Pelanggan")

        try:
            penjualan = self.repositori_penjualan.catat_penjualan(
                id_produk=produk["id_produk"],
                kuantitas_terjual=kuantitas,
                harga_satuan=harga_jual,
                catatan=catatan,
            )
            produk_diperbarui = self.repositori_produk.ambil_berdasarkan_id(produk["id_produk"])
            total_pendapatan = kuantitas * harga_jual
            print(f"\n[SUKSES] Penjualan berhasil dicatat! Total Penjualan: Rp {total_pendapatan:,.0f}")
            print(f"Sisa Stok '{produk_diperbarui['nama']}': {float(produk_diperbarui['jumlah_stok']):.2f}")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    # ==================== 5. ANALISIS PERSEDIAAN ====================
    def menu_analisis(self):
        while True:
            cetak_judul("OPTIMASI PERSEDIAAN (EOQ, SAFETY STOCK & ROP)")
            print("1. Hitung & Simpan Analisis untuk Satu Produk")
            print("2. Jalankan Analisis Otomatis untuk Seluruh Produk")
            print("3. Lihat Hasil Analisis & Rekomendasi Terakhir")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.jalankan_analisis_satu_produk()
            elif pilihan == "2":
                self.jalankan_analisis_massal()
            elif pilihan == "3":
                self.tampilkan_analisis_terbaru()

    def jalankan_analisis_satu_produk(self):
        cetak_judul("ANALISIS PERSEDIAAN PRODUK")
        self.tampilkan_produk()
        teks_id_produk = input("\nMasukkan ID Produk untuk dianalisis: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        print(f"\nParameter Optimasi untuk: {produk['nama']}")
        biaya_pemesanan = minta_angka("Biaya Pemesanan per Order (Rp) [S]", 50000.0)
        waktu_tunggu = minta_angka("Waktu Tunggu Pengiriman/Lead Time (hari) [L]", 5.0)
        rasio_biaya_simpan = minta_angka("Tarif Biaya Simpan per Tahun (% dari harga barang)", 20.0) / 100.0
        nilai_z = minta_angka("Z-score Tingkat Pelayanan (1.65 = ~95% service level)", 1.65)
        permintaan_manual = minta_angka("Permintaan Tahunan (D) - Kosongkan/0 untuk hitung otomatis dari penjualan", 0.0)

        try:
            hasil = self.layanan_persediaan.analisis_produk(
                id_produk=produk["id_produk"],
                biaya_pemesanan=biaya_pemesanan,
                rasio_biaya_penyimpanan=rasio_biaya_simpan,
                waktu_tunggu_hari=waktu_tunggu,
                skor_z=nilai_z,
                permintaan_tahunan_manual=permintaan_manual if permintaan_manual > 0 else None,
            )

            entri = hasil["analisis"]
            rekomendasi = hasil["rekomendasi"]
            biaya = hasil["biaya"]

            judul_kolom = ["Indikator", "Nilai"]
            baris_data = [
                ["Produk", f"{produk['nama']} (SKU: {produk['sku']})"],
                [
                    "Permintaan Tahunan (D)",
                    f"{float(entri['permintaan_tahunan']):,.2f} unit/tahun",
                ],
                [
                    "Biaya Pemesanan (S)",
                    f"Rp {float(entri['biaya_pemesanan']):,.2f}",
                ],
                [
                    "Biaya Simpan per Unit per Tahun (H)",
                    f"Rp {float(entri['biaya_penyimpanan_per_unit_tahun']):,.2f}",
                ],
                [
                    "Kuantitas Pesan Ekonomis (EOQ)",
                    f"{float(entri['kuantitas_pemesanan_ekonomis']):,.2f} unit",
                ],
                [
                    "Stok Pengaman (SS)",
                    f"{float(entri['stok_pengaman']):,.2f} unit",
                ],
                [
                    "Titik Pemesanan Ulang (ROP)",
                    f"{float(entri['titik_pemesanan_ulang']):,.2f} unit",
                ],
                [
                    "Frekuensi Pemesanan",
                    f"{biaya['jumlah_pemesanan_per_tahun']} kali/tahun",
                ],
                [
                    "Siklus Pemesanan",
                    f"Setiap sekitar {biaya['hari_siklus_pemesanan']} hari",
                ],
                [
                    "Total Biaya Persediaan per Tahun",
                    f"Rp {biaya['total_biaya']:,.2f}",
                ],
                [
                    "Status Stok",
                    f"{rekomendasi['status']} (stok fisik: {rekomendasi['stok_saat_ini']:.2f})",
                ],
            ]
            print("\nHASIL ANALISIS PERSEDIAAN")
            print(format_tabel(judul_kolom, baris_data))
            print(f"\nRekomendasi: {rekomendasi['tindakan']}")
            print("[Info] Hasil analisis berhasil disimpan ke tabel inventory_analysis.")
        except Exception as kesalahan:
            print(f"\n[Gagal] {kesalahan}")

    def jalankan_analisis_massal(self):
        print("\nMenjalankan analisis otomatis untuk seluruh produk...")
        daftar_hasil = self.layanan_persediaan.analisis_semua_produk()
        jumlah_berhasil = sum(1 for hasil in daftar_hasil if "kesalahan" not in hasil)
        print(f"\n[SUKSES] Selesai menganalisis {jumlah_berhasil} dari {len(daftar_hasil)} produk.")
        self.tampilkan_analisis_terbaru()

    def tampilkan_analisis_terbaru(self):
        daftar_analisis = self.repositori_analisis.ambil_semua_terbaru()
        if not daftar_analisis:
            print("\nBelum ada riwayat hasil analisis di database.")
            return

        judul_kolom = ["SKU", "Nama Produk", "Stok", "EOQ", "Safety Stock", "Reorder Point", "Status", "Tgl Analisis"]
        baris_data = []
        for entri in daftar_analisis:
            stok = float(entri["jumlah_stok"])
            titik_pemesanan_ulang = float(entri["titik_pemesanan_ulang"])
            stok_pengaman = float(entri["stok_pengaman"])
            status = tentukan_status_stok(stok, titik_pemesanan_ulang, stok_pengaman)
            teks_waktu = str(entri.get("tanggal_analisis", "-"))
            baris_data.append([
                entri["sku"],
                entri["nama_produk"][:20],
                f"{stok:.1f}",
                f"{float(entri['kuantitas_pemesanan_ekonomis']):.1f}",
                f"{stok_pengaman:.1f}",
                f"{titik_pemesanan_ulang:.1f}",
                status,
                teks_waktu,
            ])
        print("\n" + format_tabel(judul_kolom, baris_data))

    # ==================== 6. PERAMALAN (FORECASTING) ====================
    def menu_peramalan(self):
        cetak_judul("PERAMALAN PERMINTAAN (DEMAND FORECASTING)")
        self.tampilkan_produk()
        teks_id_produk = input("\nMasukkan ID Produk untuk melihat peramalan: ").strip()
        if not teks_id_produk.isdigit():
            print("ID produk tidak valid.")
            return

        produk = self.repositori_produk.ambil_berdasarkan_id(int(teks_id_produk))
        if not produk:
            print("Produk tidak ditemukan.")
            return

        penjualan_harian = self.repositori_penjualan.ambil_penjualan_harian(produk["id_produk"], hari=90)
        if not penjualan_harian:
            print(f"\nBelum ada riwayat penjualan untuk produk '{produk['nama']}' dalam 90 hari terakhir.")
            print("Peramalan memerlukan data riwayat penjualan (Menu 4).")
            return

        riwayat_kuantitas = [float(baris["total_kuantitas"]) for baris in penjualan_harian]
        statistik = hitung_statistik_permintaan(riwayat_kuantitas)

        rata_rata_3 = rata_rata_bergerak(riwayat_kuantitas, ukuran_jendela=3)
        rata_rata_7 = rata_rata_bergerak(riwayat_kuantitas, ukuran_jendela=7)
        pemulusan = pemulusan_eksponensial(riwayat_kuantitas, alfa=0.3)

        judul_kolom = ["Indikator", "Nilai"]
        baris_data = [
            ["Produk", produk["nama"]],
            ["Hari dengan Penjualan", f"{len(riwayat_kuantitas)} hari"],
            [
                "Rata-rata Permintaan Harian",
                f"{statistik['rata_rata_permintaan_harian']:.2f} unit/hari",
            ],
            [
                "Simpangan Baku Permintaan",
                f"{statistik['simpangan_baku_permintaan_harian']:.2f}",
            ],
            [
                "Proyeksi Permintaan Tahunan",
                f"{statistik['permintaan_tahunan']:,.2f} unit/tahun",
            ],
            ["Rata-rata Bergerak (3 periode)", f"{rata_rata_3:.2f} unit/hari"],
            ["Rata-rata Bergerak (7 periode)", f"{rata_rata_7:.2f} unit/hari"],
            ["Pemulusan Eksponensial (alfa 0.3)", f"{pemulusan:.2f} unit/hari"],
        ]
        print("\nHASIL PERAMALAN PERMINTAAN")
        print(format_tabel(judul_kolom, baris_data))

    # ==================== 7. LAPORAN & GRAFIK ====================
    def menu_laporan(self):
        while True:
            cetak_judul("LAPORAN & GRAFIK")
            print("1. Ringkasan Status & Nilai Inventaris")
            print("2. Laporan Produk Perlu Reorder / Kritis")
            print("3. Visualisasi Grafik Stok Barang (ASCII & PNG)")
            print("4. Ekspor Laporan Lengkap ke File Teks (output/reports/)")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                self.tampilkan_ringkasan_persediaan()
            elif pilihan == "2":
                self.tampilkan_laporan_pemesanan_ulang()
            elif pilihan == "3":
                self.tampilkan_grafik()
            elif pilihan == "4":
                self.ekspor_laporan_teks()

    def tampilkan_ringkasan_persediaan(self):
        daftar_produk = self.repositori_produk.ambil_semua()
        laporan = buat_laporan_ringkasan_persediaan(daftar_produk)
        print("\n" + laporan)

    def tampilkan_laporan_pemesanan_ulang(self):
        daftar_analisis = self.repositori_analisis.ambil_semua_terbaru()
        daftar_pemesanan_ulang = []
        for entri in daftar_analisis:
            stok = float(entri["jumlah_stok"])
            titik_pemesanan_ulang = float(entri["titik_pemesanan_ulang"])
            stok_pengaman = float(entri["stok_pengaman"])
            status = tentukan_status_stok(stok, titik_pemesanan_ulang, stok_pengaman)
            if status in ("HABIS", "KRITIS", "PERLU REORDER"):
                daftar_pemesanan_ulang.append((entri, status))

        if not daftar_pemesanan_ulang:
            print("\nSemua stok produk saat ini dalam batas aman!")
            return

        judul_kolom = ["SKU", "Nama Produk", "Stok Fisik", "Reorder Point", "EOQ (Order)", "Status"]
        baris_data = [
            [
                entri["sku"],
                entri["nama_produk"][:22],
                f"{float(entri['jumlah_stok']):.2f}",
                f"{float(entri['titik_pemesanan_ulang']):.2f}",
                f"{float(entri['kuantitas_pemesanan_ekonomis']):.0f}",
                status,
            ]
            for entri, status in daftar_pemesanan_ulang
        ]
        cetak_judul("DAFTAR PRODUK YANG HARUS DIORDER KEMBALI")
        print(format_tabel(judul_kolom, baris_data))

    def tampilkan_grafik(self):
        daftar_produk = self.repositori_produk.ambil_semua()
        if not daftar_produk:
            print("Belum ada data produk.")
            return

        # Tampilkan ASCII bar chart di terminal
        daftar_item = [(produk["nama"][:18], float(produk.get("jumlah_stok", 0))) for produk in daftar_produk]
        print(grafik_batang_ascii("GRAFIK BATANG TINGKAT STOK BARANG", daftar_item))

        # Simpan PNG chart jika matplotlib ada
        jalur_gambar_png = buat_grafik_stok(daftar_produk)
        if jalur_gambar_png:
            print(f"\n[Info] Grafik PNG berhasil dibuat dan disimpan ke: {jalur_gambar_png}")
        else:
            print("\n[Catatan] Library matplotlib tidak terinstall, grafik ditampilkan via ASCII.")

    def ekspor_laporan_teks(self):
        daftar_produk = self.repositori_produk.ambil_semua()
        isi = buat_laporan_ringkasan_persediaan(daftar_produk)
        jalur_berkas = simpan_laporan_teks(isi, awalan_nama_berkas="laporan_inventaris")
        print(f"\n[SUKSES] Laporan tersimpan di: {jalur_berkas}")

    # ==================== 8. IMPORT & EXPORT CSV ====================
    def menu_impor_ekspor(self):
        while True:
            cetak_judul("LAYANAN IMPORT & EXPORT CSV")
            print("1. Export Seluruh Data Produk ke CSV (storage/exports/backups/)")
            print("2. Export Riwayat Transaksi ke CSV (storage/exports/backups/)")
            print("3. Export Riwayat Penjualan ke CSV (storage/exports/reports/)")
            print("4. Export Hasil Analisis Optimasi ke CSV (storage/exports/reports/)")
            print("5. Import Data Produk dari CSV (storage/imports/)")
            print("6. Import Data Supplier dari CSV (storage/imports/)")
            print("7. Buat Contoh Template File CSV di storage/imports/")
            print("0. Kembali ke Menu Utama")

            pilihan = input("Pilihan: ").strip()
            if pilihan == "0":
                break
            elif pilihan == "1":
                jalur = self.layanan_ekspor.ekspor_produk_ke_csv()
                print(f"\n[SUKSES] File produk diekspor ke: {jalur}")
            elif pilihan == "2":
                jalur = self.layanan_ekspor.ekspor_transaksi_ke_csv()
                print(f"\n[SUKSES] File transaksi diekspor ke: {jalur}")
            elif pilihan == "3":
                jalur = self.layanan_ekspor.ekspor_penjualan_ke_csv()
                print(f"\n[SUKSES] File penjualan diekspor ke: {jalur}")
            elif pilihan == "4":
                jalur = self.layanan_ekspor.ekspor_analisis_persediaan_ke_csv()
                print(f"\n[SUKSES] File analisis diekspor ke: {jalur}")
            elif pilihan == "5":
                self.alur_impor_produk()
            elif pilihan == "6":
                self.alur_impor_pemasok()
            elif pilihan == "7":
                self.layanan_impor.buat_template_contoh()
                print(f"\n[SUKSES] Template dibuat di direktori: {DIREKTORI_IMPOR}")

    def alur_impor_produk(self):
        daftar_berkas = list(DIREKTORI_IMPOR.glob("*.csv"))
        if not daftar_berkas:
            print(f"\nTidak ada file CSV di direktori: {DIREKTORI_IMPOR}")
            print("Silakan letakkan file CSV Anda di direktori tersebut atau buat template (Pilihan 7).")
            return

        print("\nDaftar File CSV di folder storage/imports/:")
        for indeks, berkas in enumerate(daftar_berkas, start=1):
            print(f"  {indeks}. {berkas.name}")

        pilihan = input("Pilih nomor file: ").strip()
        if not pilihan.isdigit() or not (1 <= int(pilihan) <= len(daftar_berkas)):
            print("Pilihan nomor tidak valid.")
            return

        berkas_tujuan = daftar_berkas[int(pilihan) - 1]
        print(f"\nMemproses import dari: {berkas_tujuan.name} ...")
        berhasil, gagal, daftar_kesalahan = self.layanan_impor.impor_produk_dari_csv(berkas_tujuan)
        print(f"\n[HASIL IMPORT PRODUK]")
        print(f"- Sukses disimpan : {berhasil} baris")
        print(f"- Gagal / Duplikat: {gagal} baris")
        if daftar_kesalahan:
            print("\nRincian pesan:")
            for kesalahan in daftar_kesalahan[:10]:
                print(f"  * {kesalahan}")

    def alur_impor_pemasok(self):
        daftar_berkas = list(DIREKTORI_IMPOR.glob("*.csv"))
        if not daftar_berkas:
            print(f"\nTidak ada file CSV di direktori: {DIREKTORI_IMPOR}")
            return

        print("\nDaftar File CSV di folder storage/imports/:")
        for indeks, berkas in enumerate(daftar_berkas, start=1):
            print(f"  {indeks}. {berkas.name}")

        pilihan = input("Pilih nomor file: ").strip()
        if not pilihan.isdigit() or not (1 <= int(pilihan) <= len(daftar_berkas)):
            print("Pilihan nomor tidak valid.")
            return

        berkas_tujuan = daftar_berkas[int(pilihan) - 1]
        print(f"\nMemproses import dari: {berkas_tujuan.name} ...")
        berhasil, gagal, daftar_kesalahan = self.layanan_impor.impor_pemasok_dari_csv(berkas_tujuan)
        print(f"\n[HASIL IMPORT SUPPLIER]")
        print(f"- Sukses disimpan : {berhasil} baris")
        print(f"- Gagal / Duplikat: {gagal} baris")
        if daftar_kesalahan:
            print("\nRincian pesan:")
            for kesalahan in daftar_kesalahan[:10]:
                print(f"  * {kesalahan}")


def jalankan_cli():
    antarmuka = AntarmukaSmartStockCLI()
    antarmuka.jalankan()
