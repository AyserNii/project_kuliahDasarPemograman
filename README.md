## 1. Gambaran Proyek

**Nama:** SmartStock CLI  
**Platform:** Command Line Interface (CLI)  
**Bahasa Pemrograman:** Python  
**Database:** PostgreSQL  
**Format Import/Export:** CSV  

SmartStock merupakan aplikasi CLI untuk membantu UMKM mengelola persediaan barang dan melakukan analisis optimasi stok menggunakan metode Inventory Management.

Proyek dikembangkan menggunakan Python dengan struktur modular agar mudah dipahami, dikembangkan, diuji, dan nantinya memungkinkan untuk diperluas menjadi aplikasi berbasis web.

## 2. Tujuan

1. Membuat struktur folder Python yang rapi dan modular.
2. Memisahkan konfigurasi, koneksi database, pengelolaan data, dan proses analisis.
3. Menggunakan PostgreSQL sebagai database utama.
4. Menyediakan direktori khusus untuk kebutuhan Import dan Export CSV.
5. Menyiapkan direktori testing.
6. Memungkinkan pengembangan aplikasi secara bertahap oleh developer.

## 3. Struktur Folder Proyek

Buat struktur folder berikut secara persis:

```text
SmartStock/
│
├── main.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.sql
│   └── seed.py
│
├── repositories/
│   ├── __init__.py
│   ├── product_repository.py
│   ├── supplier_repository.py
│   ├── transaction_repository.py
│   ├── sales_repository.py
│   └── analysis_repository.py
│
├── modules/
│   ├── __init__.py
│   ├── inventory.py
│   ├── forecasting.py
│   ├── analysis.py
│   ├── validation.py
│   ├── report.py
│   └── cli_menu.py
│
├── services/
│   ├── __init__.py
│   ├── import_service.py
│   ├── export_service.py
│   └── inventory_service.py
│
├── storage/
│   ├── imports/
│   └── exports/
│       ├── reports/
│       └── backups/
│
├── output/
│   ├── reports/
│   └── charts/
│
└── tests/
    ├── __init__.py
    ├── test_inventory.py
    ├── test_validation.py
    ├── test_repository.py
    └── test_import_export.py
```

## 4. Penjelasan Fungsi Folder dan File

### A. Root Project

| File | Fungsi |
|---|---|
| `main.py` | Entry point aplikasi CLI. |
| `requirements.txt` | Daftar dependency Python. |
| `README.md` | Dokumentasi proyek dan panduan penggunaan. |
| `.env` | Menyimpan konfigurasi rahasia database. |
| `.env.example` | Contoh konfigurasi environment tanpa kredensial asli. |
| `.gitignore` | Mengatur file dan folder yang tidak boleh masuk Git. |

### B. config/

Tempat menyimpan konfigurasi aplikasi.

| File | Fungsi |
|---|---|
| `__init__.py` | Penanda package Python. |
| `settings.py` | Konfigurasi umum aplikasi dan lokasi direktori. |
| `database.py` | Konfigurasi parameter koneksi database dari environment. |

### C. database/

Tempat pengelolaan kebutuhan database PostgreSQL.

| File | Fungsi |
|---|---|
| `__init__.py` | Penanda package Python. |
| `connection.py` | Pengelolaan koneksi PostgreSQL. |
| `schema.sql` | Definisi struktur tabel dan relasi database. |
| `seed.py` | Persiapan data awal atau data contoh. |

### D. repositories/

Tempat pengelolaan komunikasi antara aplikasi dan database.

| File | Fungsi |
|---|---|
| `product_repository.py` | Operasi data produk. |
| `supplier_repository.py` | Operasi data supplier. |
| `transaction_repository.py` | Operasi transaksi persediaan. |
| `sales_repository.py` | Operasi riwayat penjualan. |
| `analysis_repository.py` | Penyimpanan dan pengambilan hasil analisis. |

Repository bertugas menangani operasi penyimpanan dan pengambilan data. Perhitungan metode inventory tidak ditempatkan di sini.

### E. modules/

Tempat modul utama aplikasi dan logika bisnis.

| File | Fungsi |
|---|---|
| `inventory.py` | Perhitungan EOQ, Safety Stock, dan Reorder Point. |
| `forecasting.py` | Modul peramalan permintaan. |
| `analysis.py` | Analisis biaya persediaan dan hasil optimasi. |
| `validation.py` | Validasi input dan data. |
| `report.py` | Penyusunan laporan dan grafik. |
| `cli_menu.py` | Pengelolaan tampilan menu dan interaksi CLI. |

### F. services/

Tempat pengelolaan proses aplikasi yang menghubungkan beberapa modul.

| File | Fungsi |
|---|---|
| `import_service.py` | Mengatur proses import data CSV ke PostgreSQL. |
| `export_service.py` | Mengatur proses export data PostgreSQL menjadi CSV. |
| `inventory_service.py` | Mengatur alur proses pengelolaan dan analisis inventory. |

### G. storage/

Tempat menyimpan file CSV yang digunakan aplikasi.

| Folder | Fungsi |
|---|---|
| `imports/` | Tempat file CSV yang akan diimpor ke database. |
| `exports/` | Tempat file hasil ekspor. |
| `exports/reports/` | Tempat laporan CSV hasil pengolahan data. |
| `exports/backups/` | Tempat file cadangan data hasil ekspor. |

**Catatan:** File CSV bukan database utama. PostgreSQL tetap menjadi sumber penyimpanan data utama.

### H. output/

Tempat menyimpan hasil keluaran aplikasi.

| Folder | Fungsi |
|---|---|
| `reports/` | Hasil laporan analisis. |
| `charts/` | Hasil visualisasi grafik. |

### I. tests/

Tempat pengujian aplikasi.

| File | Fungsi |
|---|---|
| `test_inventory.py` | Pengujian perhitungan inventory. |
| `test_validation.py` | Pengujian validasi data. |
| `test_repository.py` | Pengujian operasi repository. |
| `test_import_export.py` | Pengujian proses import dan export CSV. |

## 5. Gambaran Arsitektur

Alur komunikasi antarbagian aplikasi:

```text
              USER
                |
                v
          main.py
                |
                v
           cli_menu.py
                |
                v
            SERVICES
          /     |      \
         v      v       v
     MODULES  IMPORT  EXPORT
         |    SERVICE SERVICE
         |       |       |
         v       v       v
    REPOSITORIES  CSV   CSV
         |
         v
      DATABASE
         |
         v
     PostgreSQL
```

Prinsip arsitektur:

- CLI bertanggung jawab terhadap interaksi pengguna.
- Modules menangani logika bisnis dan perhitungan.
- Services mengatur alur proses aplikasi.
- Repositories menangani operasi database.
- PostgreSQL menjadi penyimpanan utama.
- CSV digunakan sebagai format pertukaran data dan laporan.

## 6. Ketentuan Database

Database menggunakan PostgreSQL.

Struktur tabel yang perlu disiapkan dalam rancangan:

1. `users` — data pengguna aplikasi.
2. `products` — data barang atau produk.
3. `suppliers` — data pemasok.
4. `transactions` — transaksi masuk dan keluar.
5. `sales_history` — riwayat penjualan.
6. `inventory_analysis` — riwayat hasil perhitungan optimasi stok.

Hubungan antartabel perlu menggunakan primary key dan foreign key yang sesuai.

Rancangan tabel harus mempertimbangkan konsistensi data, relasi, dan kemungkinan pengembangan aplikasi menjadi multi-user.

## 7. Ketentuan Import dan Export CSV

### Import CSV

Alur yang disiapkan:

1. Pengguna menyediakan file CSV.
2. File ditempatkan di `storage/imports/`.
3. Proses import membaca dan memvalidasi struktur file.
4. Data yang valid diteruskan ke PostgreSQL.
5. Data yang tidak valid perlu ditangani tanpa merusak data yang sudah tersimpan.

### Export CSV

Alur yang disiapkan:

1. Pengguna memilih data yang ingin diekspor.
2. Aplikasi mengambil data dari PostgreSQL.
3. Data diubah menjadi format CSV.
4. File disimpan di `storage/exports/`.
5. File dapat dibuka menggunakan Microsoft Excel atau aplikasi spreadsheet lainnya.

Import dan export merupakan dua proses berbeda.

- Import: CSV → PostgreSQL.
- Export: PostgreSQL → CSV.

## 8. Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python | Bahasa pemrograman utama. |
| PostgreSQL | Database utama. |
| psycopg | Koneksi Python dengan PostgreSQL. |
| Pandas | Pengolahan data dan CSV. |
| Matplotlib | Visualisasi grafik. |
| Rich | Tampilan CLI. |
| python-dotenv | Pengelolaan environment. |
| unittest | Pengujian aplikasi. |

## 9. Aturan Pengembangan

1. Gunakan Python sebagai bahasa pemrograman utama.
2. Aplikasi dikembangkan sebagai CLI, bukan aplikasi web.
3. Jangan menggunakan Flask, Django, atau framework web lainnya.
4. Gunakan PostgreSQL sebagai database utama.
5. Jangan menggunakan CSV sebagai pengganti database permanen.
6. Pisahkan logika perhitungan, komunikasi database, dan tampilan CLI.
7. Gunakan `.env` untuk konfigurasi database.
8. Jangan menyimpan password database di dalam source code.
9. Gunakan struktur modular agar setiap file mempunyai tanggung jawab yang jelas.
10. Jangan menghapus data historis secara otomatis.
11. Sediakan direktori khusus untuk file import dan export.
12. Pastikan file dan folder hasil keluaran dapat dikelola dengan rapi.

## 10. Batasan Pekerjaan AI Agent

**PENTING: Pada tahap ini, AI Agent hanya bertugas membuat struktur folder dan file proyek.**

AI Agent TIDAK BOLEH:

- Menuliskan implementasi kode Python.
- Membuat fungsi perhitungan EOQ, Safety Stock, atau ROP.
- Membuat implementasi CRUD.
- Membuat implementasi koneksi database.
- Membuat query SQL secara otomatis.
- Membuat algoritma forecasting.
- Membuat implementasi Import dan Export CSV.
- Membuat isi file Python dengan kode contoh atau placeholder implementasi.

AI Agent BOLEH:

- Membuat seluruh folder sesuai struktur.
- Membuat file kosong sesuai daftar.
- Membuat `__init__.py` kosong.
- Membuat `requirements.txt` kosong.
- Membuat `.env.example` sebagai file konfigurasi contoh tanpa kredensial asli.
- Membuat `README.md` dengan penjelasan singkat struktur proyek.
- Membuat `schema.sql` kosong untuk disiapkan developer.

Semua implementasi program akan ditulis sendiri oleh developer secara bertahap.

## 11. Acceptance Criteria

Pekerjaan dianggap selesai apabila:

- [ ] Folder utama `SmartStock/` berhasil dibuat.
- [ ] Seluruh subfolder sesuai struktur tersedia.
- [ ] Seluruh file yang tercantum tersedia.
- [ ] Semua folder memiliki fungsi sesuai dokumentasi.
- [ ] Tidak ada implementasi kode Python otomatis.
- [ ] Tidak ada kredensial database asli.
- [ ] Struktur siap digunakan untuk pengembangan manual.
- [ ] Aplikasi belum perlu dijalankan karena belum ada implementasi kode.

## 12. Hasil Akhir yang Diharapkan

AI Agent harus menghasilkan sebuah direktori proyek SmartStock yang rapi, lengkap, dan siap dikembangkan.

Developer akan mengisi kode Python, SQL, dan implementasi fitur sendiri secara bertahap.

**Fokus utama tahap ini adalah membangun fondasi struktur proyek, bukan membangun aplikasinya.**