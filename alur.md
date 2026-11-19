# Dokumentasi Arsitektur, Alur Sistem, dan Fungsi File SmartStock CLI

Dokumen ini menjelaskan secara menyeluruh arsitektur, peran setiap direktori dan file, pemanfaatan library **Pandas**, serta alur kerja sistem pada aplikasi **SmartStock CLI**.

---

## 1. Gambaran Umum & Arsitektur Sistem

SmartStock CLI mengadopsi prinsip arsitektur berlapis (*layered modular architecture*) yang memisahkan tanggung jawab antara:
1. **Presentation Layer (CLI Interface)**: Menangani interaksi dengan pengguna.
2. **Business & Domain Logic Layer (Modules)**: Menangani kalkulasi matematis inventory, peramalan, dan validasi data.
3. **Application & Orchestration Layer (Services)**: Mengatur alur proses multi-langkah, seperti kalkulasi batch, serta proses import dan export data.
4. **Data Access Layer (Repositories)**: Menangani seluruh komunikasi query SQL dengan database PostgreSQL.
5. **Persistence Layer**: Database PostgreSQL sebagai basis data utama, serta file CSV di direktori `storage/` sebagai media pertukaran data.

### Diagram Alur Komunikasi Sistem

```text
                     PENGGUNA (USER)
                           |
                           v
                        main.py
                           |
                           v
                  modules/cli_menu.py
                           |
            +--------------+--------------+
            |                             |
            v                             v
        SERVICES                       MODULES
   (import / export /           (inventory, forecasting,
    inventory_service)           analysis, validation, report)
            |                             |
            +--------------+--------------+
                           |
                           v
                     REPOSITORIES
           (product, supplier, transaction,
             sales, analysis_repository)
                           |
                           v
                       DATABASE
                     (PostgreSQL)
```

---

## 2. Pemanfaatan Library Pandas dalam Proyek

Sesuai materi perkuliahan Dasar Pemrograman (Pertemuan 7: *Matrix dan Library Pandas*), library **Pandas** diintegrasikan ke dalam sistem untuk:

1. **Import Data CSV (`services/import_service.py`)**:
   - Menggunakan fungsi bawaan `pd.read_csv(file_path)` untuk membaca dataset produk dan supplier dari file CSV menjadi objek `pandas.DataFrame`.
   - Menggunakan fitur `.fillna("")` dan iterasi `.iterrows()` untuk memvalidasi dan memetakan record secara terstruktur sebelum disimpan ke PostgreSQL.
2. **Export Data ke CSV (`services/export_service.py`)**:
   - Mengubah list dictionary hasil query database menjadi `pandas.DataFrame(data)`.
   - Menyimpan DataFrame ke file CSV menggunakan metode `.to_csv(filepath, index=False)`.
3. **Template Generator (`services/import_service.py`)**:
   - Membuat template CSV contoh menggunakan dictionary yang dikonversi ke DataFrame (`pd.DataFrame(data_dict)`).
4. **Analisis Deret Waktu & Peramalan (`modules/forecasting.py`)**:
   - Menggunakan `pd.Series(data).rolling(window=window_size).mean()` untuk menghitung pergerakan rata-rata permintaan penjualan (*moving average*).
5. **Penyajian Data Tabel (`modules/report.py`)**:
   - Menyediakan fungsi `dataframe_to_string_table(df)` untuk memformat DataFrame menjadi representasi teks tabel yang rapi di CLI.

---

## 3. Penjelasan Struktur Folder dan Fungsi Setiap File

### A. Root Project
- [`main.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/main.py): Titik masuk (*entry point*) aplikasi CLI yang menyambut pengguna, menginisialisasi menu utama, serta menangani *exception* global (`KeyboardInterrupt`).
- [`requirements.txt`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/requirements.txt): Daftar pustaka dependensi (`psycopg[binary]`, `python-dotenv`, `pandas`).
- [`README.md`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/README.md): Dokumen Product Requirement Document (PRD) asli.
- [`alur.md`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/alur.md): Dokumen teknis penjelasan arsitektur, alur data, dan fungsi file.
- [`.env`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/.env): Menyimpan variabel rahasia koneksi database (`DATABASE_URL`).
- [`.env.example`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/.env.example): Contoh variabel lingkungan tanpa kredensial asli.
- [`.gitignore`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/.gitignore): Mengatur file virtual environment, cache, dan file sensitif yang diabaikan Git.

### B. Folder `config/`
- [`config/settings.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/config/settings.py):
  - Mengatur path absolut ke folder `storage/`, `output/`, dan subdirektorinya.
  - Memastikan folder runtime otomatis dibuat saat program berjalan.
  - Menyimpan konstanta bisnis default: Hari kerja setahun (365 hari), Biaya Pemesanan default (Rp 50.000), Rasio Biaya Simpan (20%/tahun), Lead Time default (5 hari), dan Z-Score Service Level (1.65).
- [`config/database.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/config/database.py):
  - Membaca environment file `.env` dan menyediakan fungsi `get_database_url()`.

### C. Folder `database/`
- [`database/connection.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/database/connection.py):
  - Mengelola koneksi ke database PostgreSQL menggunakan `psycopg.connect`.
- [`database/schema.sql`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/database/schema.sql):
  - Definisi DDL seluruh tabel:
    1. `users`: Akun pengguna aplikasi.
    2. `suppliers`: Data mitra pemasok barang.
    3. `products`: Master produk (SKU, nama, stok, harga beli/jual, stok minimum).
    4. `transactions`: Transaksi perpindahan stok (`IN` untuk masuk, `OUT` untuk keluar).
    5. `sales_history`: Riwayat transaksi penjualan ke konsumen.
    6. `inventory_analysis`: Riwayat hasil kalkulasi optimasi EOQ, Safety Stock, dan ROP.
- [`database/seed.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/database/seed.py):
  - Menjalankan file `schema.sql` dan memasukkan data sampel awal (pemasok, produk, transaksi, riwayat penjualan, dan hasil analisis).

### D. Folder `repositories/` (Data Access Layer)
Repository bertanggung jawab mengeksekusi perintah SQL (CRUD) dan mengembalikan hasil dalam format dictionary (`psycopg.rows.dict_row`):
- [`product_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/product_repository.py):
  - Mengambil semua produk, mencari berdasarkan ID atau SKU, menambah produk baru, mengedit data produk, memperbarui stok fisik, menghapus produk, dan memfilter produk dengan stok menipis (`stock_quantity <= minimum_stock`).
- [`supplier_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/supplier_repository.py):
  - Mengambil daftar supplier, mencari berdasarkan ID atau kode supplier, menambah, mengubah, dan menghapus data pemasok.
- [`transaction_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/transaction_repository.py):
  - Mencatat riwayat transaksi persediaan (`IN` / `OUT`).
  - Secara transaksional memperbarui `stock_quantity` produk (+ jika `IN`, - jika `OUT`).
  - Mencegah stok menjadi minus jika kuantitas `OUT` melebihi stok yang ada.
- [`sales_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/sales_repository.py):
  - Mencatat penjualan baru ke `sales_history` sekaligus membuat transaksi `OUT` dan mengurangi stok produk.
  - Fungsi `get_daily_sales()` mengagregasi data penjualan per tanggal untuk kebutuhan perhitungan peramalan permintaan.
- [`analysis_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/analysis_repository.py):
  - Menyimpan hasil optimasi inventaris (`eoq`, `safety_stock`, `reorder_point`) ke tabel `inventory_analysis` menggunakan mekanisme `ON CONFLICT DO UPDATE`.
  - Mengambil riwayat analisis terkini untuk masing-masing produk.

### E. Folder `modules/` (Business Logic & Calculations)
- [`inventory.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/inventory.py):
  - `calculate_eoq(D, S, H)`: Menghitung kuantitas pemesanan ekonomis:
    $$\text{EOQ} = \sqrt{\frac{2 \times D \times S}{H}}$$
  - `calculate_safety_stock(stddev, L, Z)`: Menghitung stok pengaman untuk mengantisipasi ketidakpastian permintaan selama waktu tunggu:
    $$\text{SS} = Z \times \sigma_d \times \sqrt{L}$$
  - `calculate_reorder_point(avg_demand, L, SS)`: Menghitung titik batas stok untuk memesan kembali:
    $$\text{ROP} = (d \times L) + \text{SS}$$
  - `calculate_inventory_costs(...)`: Menghitung biaya simpan tahunan, biaya pesan tahunan, dan total biaya variabel persediaan.
- [`forecasting.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/forecasting.py):
  - `moving_average()`: Peramalan permintaan periode berikutnya berbasis rata-rata bergerak.
  - `pandas_rolling_forecast()`: Menghitung deret moving average menggunakan `pandas.Series.rolling()`.
  - `weighted_moving_average()`: Moving average berbobot.
  - `exponential_smoothing()`: Pemulusan eksponensial tunggal (Single Exponential Smoothing).
  - `calculate_demand_statistics()`: Menghitung rata-rata permintaan harian, standar deviasi, dan proyeksi permintaan tahunan.
- [`analysis.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/analysis.py):
  - `determine_stock_status()`: Menentukan status kesehatan stok (`HABIS`, `KRITIS`, `PERLU REORDER`, atau `AMAN`).
  - `compare_inventory_policies()`: Membandingkan total biaya kebijakan pemesanan konvensional vs kebijakan EOQ dan menghitung persentase penghematan biaya.
  - `generate_recommendation()`: Menghasilkan rekomendasi tindakan konkret untuk staf gudang/manajer inventaris.
- [`validation.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/validation.py):
  - Validasi angka positif, angka non-negatif, string wajib isi, format SKU, tipe transaksi, dan format tanggal.
- [`report.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/report.py):
  - Format tabel bergaris ASCII (`format_table`).
  - Integrasi representasi tabel Pandas DataFrame (`dataframe_to_string_table`).
  - Penyusunan ringkasan aset inventaris dan penyimpanan ke file teks di [`output/reports/`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/output/reports/).
  - Visualisasi grafik batang di terminal (ASCII bar chart) serta dukungan pembuatan grafik PNG jika `matplotlib` tersedia.
- [`cli_menu.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/cli_menu.py):
  - Mengelola menu interaktif konsol dengan 8 opsi utama yang memandu pengguna langkah demi langkah.

### F. Folder `services/` (Application Services)
- [`import_service.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/services/import_service.py):
  - Membaca file CSV dari `storage/imports/` menggunakan `pandas.read_csv`.
  - Memvalidasi data baris demi baris dan menyimpannya ke database PostgreSQL.
  - Menghasilkan file template CSV (`template_products.csv` dan `template_suppliers.csv`) menggunakan Pandas.
- [`export_service.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/services/export_service.py):
  - Mengambil data dari repositori PostgreSQL, membungkusnya ke dalam `pandas.DataFrame`, dan mengekspornya ke CSV di `storage/exports/backups/` atau `storage/exports/reports/`.
- [`inventory_service.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/services/inventory_service.py):
  - Mengatur alur kalkulasi optimasi inventaris: mengambil parameter produk & riwayat penjualan, menghitung statistik demand harian, memanggil modul kalkulasi inventory, dan menyimpan hasilnya ke database `inventory_analysis`.

### G. Folder `storage/` dan `output/`
- `storage/imports/`: Tempat meletakkan file CSV yang akan diimpor ke PostgreSQL.
- `storage/exports/backups/`: Tempat file cadangan data produk dan transaksi hasil ekspor.
- `storage/exports/reports/`: Tempat file laporan penjualan dan analisis inventory format CSV.
- `output/reports/`: Tempat penyimpanan laporan teks analisis dan inventaris.
- `output/charts/`: Tempat penyimpanan gambar grafik hasil visualisasi (misal format PNG).

### H. Folder `tests/` (Automated Testing)
- [`test_inventory.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/tests/test_inventory.py): Pengujian unit kalkulasi EOQ, Safety Stock, Reorder Point, dan biaya persediaan.
- [`test_validation.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/tests/test_validation.py): Pengujian unit fungsi validasi input.
- [`test_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/tests/test_repository.py): Pengujian integrasi CRUD produk dan supplier di PostgreSQL.
- [`test_import_export.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/tests/test_import_export.py): Pengujian proses import dan export CSV menggunakan Pandas.
- [`test_database_seed.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/tests/test_database_seed.py): Pengujian konsistensi data contoh awal.

---

## 4. Alur Kerja Fitur-Fitur Utama

### A. Alur Pencatatan Transaksi Masuk (IN) & Keluar (OUT)
1. Pengguna memilih menu **3 (Transaksi Persediaan)** di CLI.
2. Pengguna memilih produk dari daftar dan memasukkan jumlah kuantitas serta biaya/harga satuan.
3. `cli_menu.py` memanggil `transaction_repo.create()`.
4. Repositori memulai transaksi PostgreSQL:
   - Jika tipe `OUT`, sistem mengecek apakah stok mencukupi (menggunakan `SELECT ... FOR UPDATE`).
   - Menyimpan record transaksi ke tabel `transactions`.
   - Mengubah kolom `stock_quantity` pada tabel `products` secara otomatis.
   - Komit transaksi database.
5. CLI menampilkan pesan sukses beserta jumlah stok fisik terbaru.

### B. Alur Pencatatan Penjualan (Sales)
1. Pengguna memilih menu **4 (Riwayat Penjualan)** -> **Catat Penjualan Baru**.
2. Pengguna menginput ID produk, jumlah terjual, dan harga jual satuan.
3. `cli_menu.py` memanggil `sales_repo.record_sale()`.
4. Repositori secara atomik:
   - Membuat baris transaksi `OUT` pada tabel `transactions`.
   - Mengurangi stok produk di tabel `products`.
   - Menyimpan data penjualan pada tabel `sales_history` dengan mereferensikan `transaction_id`.
5. Data penjualan siap digunakan sebagai basis data histori permintaan (*demand forecasting*).

### C. Alur Perhitungan & Optimasi Inventory (EOQ & ROP)
1. Pengguna memilih menu **5 (Analisis Persediaan)**.
2. Pengguna dapat memilih analisis produk tertentu atau *batch analysis* seluruh produk.
3. `inventory_service.py` mengambil data historis penjualan harian dari `sales_repository`.
4. `forecasting.py` menghitung rata-rata permintaan harian ($d$) dan standar deviasi permintaan ($\sigma_d$).
5. `inventory.py` menghitung:
   - $\text{EOQ} = \sqrt{\frac{2 \times D \times S}{H}}$
   - $\text{Safety Stock} = Z \times \sigma_d \times \sqrt{L}$
   - $\text{Reorder Point} = (d \times L) + \text{SS}$
6. `analysis_repo.save()` menyimpan hasil kalkulasi ke tabel `inventory_analysis`.
7. `analysis.py` mengevaluasi status stok barang saat ini dan mengeluarkan rekomendasi tindakan pemesanan.

### D. Alur Import Data CSV Menggunakan Pandas
1. File CSV diletakkan di folder `storage/imports/` (contoh: `template_products.csv`).
2. Pengguna memilih menu **8 (Import & Export Data CSV)** -> **Import Produk**.
3. `import_service.py` membaca file menggunakan `pandas.read_csv()`.
4. Setiap baris DataFrame divalidasi format SKU, nilai numerik stok, dan harga.
5. Baris yang valid dimasukkan ke tabel `products` di PostgreSQL, sedangkan baris yang duplikat atau bermasalah dilaporkan ke pengguna tanpa menggagalkan baris lain.

### E. Alur Export Data ke CSV Menggunakan Pandas
1. Pengguna memilih data yang ingin diekspor (Produk / Transaksi / Penjualan / Hasil Analisis).
2. Repositori mengambil data dari PostgreSQL.
3. Data dikonversi ke `pandas.DataFrame`.
4. DataFrame disimpan dalam format file `.csv` di folder `storage/exports/`. File ini dapat langsung dibuka di spreadsheet (Excel, Google Sheets, LibreOffice Calc).

---

## 5. Cara Menjalankan Aplikasi dan Testing

### Menjalankan Aplikasi CLI
Buka terminal dan jalankan:
```powershell
.venv\Scripts\python.exe main.py
```

### Menjalankan Seluruh Unit Test Otomatis
```powershell
.venv\Scripts\python.exe -m unittest discover tests
```
Seluruh pengujian unit (20 test cases) dirancang untuk memverifikasi keakuratan kalkulasi matematis, kepatuhan validasi, integritas operasi database, dan pertukaran data Pandas CSV.
