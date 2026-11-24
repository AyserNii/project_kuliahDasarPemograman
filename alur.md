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
   - Peramalan permintaan tahunan dihitung dengan regresi linear metode Least Squares.
5. **Penyajian Data Tabel (`modules/report.py`)**:
   - Menyediakan fungsi `ubah_dataframe_ke_tabel_teks(kerangka_data)` untuk memformat DataFrame menjadi representasi teks tabel yang rapi di CLI.

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
  - Menyimpan konstanta bisnis default sesuai jurnal: 26 hari kerja per bulan (312 hari per tahun), biaya pemesanan Rp 90.000, rasio biaya simpan 10%/tahun, dan lead time 2 hari.
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
  - Nama kolom menggunakan bahasa Indonesia; skema juga mengganti nama kolom lama secara otomatis tanpa menghapus datanya.
- [`database/seed.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/database/seed.py):
  - Menjalankan file `schema.sql` dan memasukkan data sampel awal (pemasok, produk, transaksi, riwayat penjualan, dan hasil analisis).

### D. Folder `repositories/` (Data Access Layer)
Repository bertanggung jawab mengeksekusi perintah SQL (CRUD) dan mengembalikan hasil dalam format dictionary (`psycopg.rows.dict_row`):
- [`product_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/product_repository.py):
  - Mengambil semua produk, mencari berdasarkan ID atau SKU, menambah produk baru, mengedit data produk, memperbarui stok fisik, menghapus produk, dan memfilter produk dengan stok menipis (`jumlah_stok <= stok_minimum`).
- [`supplier_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/supplier_repository.py):
  - Mengambil daftar supplier, mencari berdasarkan ID atau kode supplier, menambah, mengubah, dan menghapus data pemasok.
- [`transaction_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/transaction_repository.py):
  - Mencatat riwayat transaksi persediaan (`IN` / `OUT`).
  - Secara transaksional memperbarui `jumlah_stok` produk (+ jika `IN`, - jika `OUT`).
  - Mencegah stok menjadi minus jika kuantitas `OUT` melebihi stok yang ada.
- [`sales_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/sales_repository.py):
  - Mencatat penjualan baru ke `sales_history` sekaligus membuat transaksi `OUT` dan mengurangi stok produk.
  - Fungsi `ambil_permintaan_tahunan()` mengagregasi penjualan per tahun untuk kebutuhan regresi linear.
- [`analysis_repository.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/repositories/analysis_repository.py):
  - Menyimpan hasil optimasi persediaan (`kuantitas_pemesanan_ekonomis`, `stok_pengaman`, `titik_pemesanan_ulang`) ke tabel `inventory_analysis` menggunakan mekanisme `ON CONFLICT DO UPDATE`.
  - Mengambil riwayat analisis terkini untuk masing-masing produk.

### E. Folder `modules/` (Business Logic & Calculations)
- [`inventory.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/inventory.py):
  - `hitung_kuantitas_pemesanan_ekonomis(permintaan_tahunan, biaya_pemesanan, biaya_penyimpanan_per_unit_tahun)`: Menghitung kuantitas pemesanan ekonomis:
    $$\text{EOQ} = \sqrt{\frac{2 \times D \times S}{H}}$$
  - `hitung_stok_pengaman(pemakaian_harian, waktu_tunggu_hari)`: Menghitung stok pengaman sesuai jurnal, `SS = pemakaian harian × waktu tunggu`, dibulatkan ke atas ke unit utuh.
  - `hitung_titik_pemesanan_ulang(rata_rata_permintaan_harian, waktu_tunggu_hari, stok_pengaman)`: Menghitung titik batas stok untuk memesan kembali:
    $$\text{ROP} = (d \times L) + \text{SS}$$
  - `hitung_biaya_persediaan(...)`: Menghitung biaya simpan tahunan, biaya pesan tahunan, dan total biaya variabel persediaan.
- [`forecasting.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/forecasting.py):
  - `buat_peramalan_regresi_linear()`: Menghitung garis tren Least Squares dari data permintaan tahunan dan memproyeksikan tiga tahun selanjutnya. Tahun yang tidak memiliki catatan di antara rentang data dihitung 0; permintaan tahun berjalan disetarakan ke estimasi tahunan memakai basis 26 hari kerja per bulan.
- [`analysis.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/analysis.py):
  - `tentukan_status_stok()`: Menentukan status kesehatan stok (`HABIS`, `KRITIS`, `PERLU REORDER`, atau `AMAN`).
  - `bandingkan_kebijakan_persediaan()`: Membandingkan total biaya kebijakan pemesanan konvensional vs kebijakan EOQ dan menghitung persentase penghematan biaya.
  - `buat_rekomendasi()`: Menghasilkan rekomendasi tindakan konkret untuk staf gudang/manajer persediaan.
- [`validation.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/validation.py):
  - Validasi angka positif, angka non-negatif, string wajib isi, format SKU, tipe transaksi, dan format tanggal.
- [`report.py`](file:///c:/Users/Resya%20Anggara/project_kuliahDasarPemograman/modules/report.py):
  - Format tabel bergaris ASCII (`format_tabel`).
  - Integrasi representasi tabel Pandas DataFrame (`ubah_dataframe_ke_tabel_teks`).
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
  - Mengatur alur kalkulasi optimasi inventaris: mengambil data permintaan tahunan, membuat proyeksi tiga tahun, menghitung EOQ/SS/ROP setiap tahun, lalu menyimpan proyeksi tahun pertama ke `inventory_analysis`.

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

## 4. Rumus Penting per Menu

Rumus yang menghasilkan angka ditampilkan berikut. Menu administratif yang tidak melakukan kalkulasi memiliki keterangan **tidak ada rumus bisnis khusus**.

| Menu / halaman | Rumus atau aturan yang dipakai |
|---|---|
| **Dashboard (GUI)** | Total unit = $\sum$ stok. Produk habis jika stok $\leq 0$; perlu reorder jika $0 < \text{stok} \leq \text{stok minimum}$; selain itu aman. |
| **1. Kelola Produk** | Tidak ada rumus bisnis khusus. Data stok dan harga dicatat; nilai aset stok dihitung di laporan: $\text{stok} \times \text{biaya satuan}$. |
| **2. Kelola Supplier** | Tidak ada rumus bisnis khusus; menu ini mengelola data pemasok. |
| **3. Transaksi Persediaan** | Stok baru = stok lama + kuantitas IN; stok baru = stok lama − kuantitas OUT. Transaksi OUT ditolak jika kuantitasnya melebihi stok tersedia. |
| **4. Riwayat Penjualan** | Total penjualan per transaksi = kuantitas terjual $\times$ harga jual per unit. Stok baru = stok lama − kuantitas terjual; total pendapatan pada halaman penjualan = $\sum$ total transaksi yang dimuat. |
| **5. Analisis Persediaan** | Demand harian $d = D/312$; biaya simpan per unit per tahun $H = \text{biaya satuan} \times \text{rasio biaya simpan}$. EOQ $Q^* = \sqrt{(2DS)/H}$. Safety Stock $SS = \lceil dL \rceil$. Reorder Point $ROP = (dL)+SS$. Frekuensi pesanan = $D/Q^*$; biaya pesan tahunan = $(D/Q^*)S$; biaya simpan tahunan = $(Q^*/2)H$; total biaya variabel = biaya pesan + biaya simpan. Siklus pemesanan dalam hari kerja = $(Q^*/D)\times312$. Status: HABIS jika stok $\leq0$; KRITIS jika $SS>0$ dan stok $\leq SS$; PERLU REORDER jika stok $\leq ROP$; selainnya AMAN. |
| **6. Peramalan Permintaan** | Least Squares: $b = \sum((x-\bar{x})(y-\bar{y}))/\sum((x-\bar{x})^2)$; $a = \bar{y}-b\bar{x}$; garis tren $y=a+bx$. $x$ adalah urutan periode tahunan dan $y$ adalah permintaan tahunan. Aplikasi memproyeksikan tiga periode berikutnya. Untuk tahun berjalan, estimasi tahunan = penjualan sampai saat ini $\times 312/\text{hari kerja yang telah berjalan}$, dengan hari kerja berjalan $=(\text{bulan}-1)\times26+\min(\text{tanggal},26)$; sela tahun tanpa catatan diisi 0. |
| **7. Laporan & Grafik** | Nilai aset stok = $\sum(\text{stok} \times \text{biaya satuan})$; total kuantitas = $\sum \text{stok}$; jumlah produk menipis = hitung produk dengan stok $\leq$ stok minimum. Grafik hanya memvisualisasikan nilai stok/penjualan. |
| **8. Import & Export CSV** | Tidak ada rumus bisnis khusus; data dibaca, divalidasi, lalu dipindahkan antara CSV dan database. |

Parameter awal analisis mengikuti acuan jurnal: 26 hari kerja/bulan (312 hari/tahun), biaya pesan Rp90.000/order, biaya simpan 10% dari biaya satuan per tahun, dan lead time 2 hari. Nilai dapat berbeda dari tabel jurnal karena aplikasi menghitungnya dari data produk dan penjualan yang tersimpan.

## 5. Alur Kerja Fitur-Fitur Utama

### A. Alur Pencatatan Transaksi Masuk (IN) & Keluar (OUT)
1. Pengguna memilih menu **3 (Transaksi Persediaan)** di CLI.
2. Pengguna memilih produk dari daftar dan memasukkan jumlah kuantitas serta biaya/harga satuan.
3. `cli_menu.py` memanggil `transaction_repo.create()`.
4. Repositori memulai transaksi PostgreSQL:
   - Jika tipe `OUT`, sistem mengecek apakah stok mencukupi (menggunakan `SELECT ... FOR UPDATE`).
   - Menyimpan record transaksi ke tabel `transactions`.
   - Mengubah kolom `jumlah_stok` pada tabel `products` secara otomatis.
   - Komit transaksi database.
5. CLI menampilkan pesan sukses beserta jumlah stok fisik terbaru.

### B. Alur Pencatatan Penjualan (Sales)
1. Pengguna memilih menu **4 (Riwayat Penjualan)** -> **Catat Penjualan Baru**.
2. Pengguna menginput ID produk, jumlah terjual, dan harga jual satuan.
3. `cli_menu.py` memanggil `repositori_penjualan.catat_penjualan()`.
4. Repositori secara atomik:
   - Membuat baris transaksi `OUT` pada tabel `transactions`.
   - Mengurangi stok produk di tabel `products`.
   - Menyimpan data penjualan pada tabel `sales_history` dengan mereferensikan `id_transaksi`.
5. Data penjualan siap digunakan sebagai basis data histori permintaan (*demand forecasting*).

### C. Alur Perhitungan & Optimasi Inventory (EOQ & ROP)
1. Pengguna memilih menu **5 (Analisis Persediaan)**.
2. Pengguna dapat memilih analisis produk tertentu atau *batch analysis* seluruh produk.
3. `inventory_service.py` mengambil permintaan tahunan per produk dari `sales_repository`.
4. `forecasting.py` menghitung proyeksi tiga tahun dengan Least Squares (`y = a + bx`). Permintaan harian diperoleh dari proyeksi tahunan dibagi 12 bulan × 26 hari kerja.
5. `inventory.py` menghitung:
   - $\text{EOQ} = \sqrt{\frac{2 \times D \times S}{H}}$
   - $\text{Safety Stock} = \lceil d \times L \rceil$
   - $\text{Reorder Point} = (d \times L) + \text{SS}$
6. Ketiga proyeksi ditampilkan di CLI/GUI; proyeksi tahun pertama disimpan ke tabel `inventory_analysis`.
7. `analysis.py` mengevaluasi status stok barang saat ini dan mengeluarkan rekomendasi tindakan pemesanan.

### D. Alur Peramalan Permintaan
1. Pengguna memilih menu **6 (Peramalan Permintaan)** atau halaman **Peramalan** pada GUI.
2. `sales_repository` mengambil jumlah penjualan per tahun.
3. `buat_peramalan_regresi_linear()` menghitung kemiringan ($b$), intersep ($a$), dan nilai ramalan tiga tahun berikutnya.
4. CLI dan GUI menampilkan persamaan tren serta nilai permintaan tahunan yang sama.

### E. Alur Laporan & Grafik
1. Pengguna memilih menu **7 (Laporan & Visualisasi Grafik)** atau halaman **Laporan** pada GUI.
2. Sistem menghitung jumlah unit, nilai aset berdasarkan biaya satuan, dan jumlah produk di/bawah stok minimum.
3. Ringkasan dapat ditampilkan/disimpan sebagai teks; grafik stok dapat dibuat sebagai ASCII atau PNG.

### F. Alur Import Data CSV Menggunakan Pandas
1. File CSV diletakkan di folder `storage/imports/` (contoh: `template_products.csv`).
2. Pengguna memilih menu **8 (Import & Export Data CSV)** -> **Import Produk**.
3. `import_service.py` membaca file menggunakan `pandas.read_csv()`.
4. Setiap baris DataFrame divalidasi format SKU, nilai numerik stok, dan harga.
5. Baris yang valid dimasukkan ke tabel `products` di PostgreSQL, sedangkan baris yang duplikat atau bermasalah dilaporkan ke pengguna tanpa menggagalkan baris lain.

### G. Alur Export Data ke CSV Menggunakan Pandas
1. Pengguna memilih data yang ingin diekspor (Produk / Transaksi / Penjualan / Hasil Analisis).
2. Repositori mengambil data dari PostgreSQL.
3. Data dikonversi ke `pandas.DataFrame`.
4. DataFrame disimpan dalam format file `.csv` di folder `storage/exports/`. File ini dapat langsung dibuka di spreadsheet (Excel, Google Sheets, LibreOffice Calc).

---

## 6. Cara Menjalankan Aplikasi dan Testing

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
