# SmartStock

SmartStock adalah aplikasi desktop/CLI untuk pengelolaan persediaan UMKM. Aplikasi menyediakan pengelolaan produk, pemasok, transaksi masuk dan keluar, penjualan, analisis EOQ/ROP/Safety Stock, peramalan permintaan, laporan, serta impor dan ekspor CSV.

## Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python 3 | Bahasa pemrograman utama |
| Tkinter / ttk | Antarmuka desktop GUI |
| PostgreSQL | Penyimpanan data utama |
| psycopg 3 | Koneksi Python ke PostgreSQL |
| python-dotenv | Membaca konfigurasi database dari `.env` |
| Pandas | Pemrosesan dan pertukaran data CSV |
| unittest | Pengujian aplikasi bawaan Python |
| Matplotlib (opsional) | Pembuatan grafik PNG pada laporan |

## Persyaratan Instalasi

Pastikan perangkat telah memiliki:

1. **Python 3.10 atau lebih baru**
   - Saat menginstal Python di Windows, aktifkan **Add python.exe to PATH**.
   - Pastikan `pip` tersedia.
2. **PostgreSQL**
   - Diperlukan PostgreSQL 13 atau lebih baru beserta layanan/server PostgreSQL yang aktif.
3. **Tkinter**
   - Sudah termasuk pada instalasi Python standar untuk Windows.
   - Jika module `_tkinter` tidak tersedia, pasang ulang Python dengan komponen Tkinter/Tcl.

## Instalasi

Buka terminal/PowerShell di folder proyek, kemudian jalankan:

```powershell
# Buat virtual environment
py -m venv .venv

# Aktifkan virtual environment
.venv\Scripts\Activate.ps1

# Perbarui pip
python -m pip install --upgrade pip

# Instal dependency aplikasi
pip install -r requirements.txt
```

Jika PowerShell menolak menjalankan skrip aktivasi, jalankan:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Konfigurasi Database

1. Buat database PostgreSQL, misalnya bernama `smartstock`.
2. Salin contoh environment:

```powershell
Copy-Item .env.example .env
```

3. Isi `.env` dengan URL koneksi PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:PASSWORD_ANDA@localhost:5432/smartstock
```

Sesuaikan nama pengguna, password, host, port, dan nama database.

> Jangan commit file `.env` karena berisi kredensial database.

## Persiapan Skema dan Data Contoh

Jalankan seed sekali untuk membuat tabel dan mengisi data contoh:

```powershell
python -m database.seed
```

Perintah tersebut menggunakan `database/schema.sql`, lalu menambahkan data pemasok, produk, transaksi, penjualan, dan hasil analisis contoh.

## Menjalankan Aplikasi

Mode GUI adalah mode bawaan:

```powershell
python main.py
```

Untuk menjalankan mode CLI:

```powershell
python main.py --cli
```

Jika GUI gagal dibuat atau library grafik GUI tidak tersedia, `main.py` akan mencoba menjalankan mode CLI sebagai alternatif.

## Pemecahan Masalah

### Perintah `py` atau `python` tidak dikenali

Pastikan Python 3.10 atau lebih baru sudah terpasang dan opsi **Add python.exe to PATH** dipilih saat instalasi. Tutup lalu buka kembali PowerShell, kemudian periksa:

```powershell
py --version
python --version
```

### Aktivasi virtual environment ditolak PowerShell

Izinkan skrip hanya untuk sesi PowerShell saat ini, lalu aktifkan kembali:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Dependency tidak ditemukan saat aplikasi dijalankan

Pastikan virtual environment aktif (biasanya prompt diawali `(.venv)`), lalu pasang ulang dependency:

```powershell
python -m pip install -r requirements.txt
```

### `python main.py` malah masuk ke CLI

GUI adalah mode bawaan; CLI hanya dipilih jika aplikasi menerima argumen `--cli`. Jalankan dari folder utama proyek tanpa argumen tersebut:

```powershell
python main.py
```

Jika CLI tetap terbuka, pastikan PowerShell berada di folder proyek dan file `main.py` yang dijalankan adalah milik proyek ini:

```powershell
Get-Location
Resolve-Path .\main.py
Select-String -Path .\main.py -Pattern '--cli|Gagal membuka antarmuka GUI|Menjalankan dalam mode CLI'
```

Pada `main.py` proyek ini, kegagalan membuka GUI seharusnya menampilkan pesan `Gagal membuka antarmuka GUI` sebelum mencoba CLI. Jika pesan tersebut tidak muncul, periksa apakah terminal atau konfigurasi Run/Debug VS Code menjalankan file atau versi proyek yang berbeda.

Periksa juga apakah Tkinter tersedia pada interpreter Python yang digunakan:

```powershell
python -c "import tkinter; print('Tkinter tersedia:', tkinter.TkVersion)"
```

Jika perintah itu gagal, instal atau ubah instalasi Python di Windows dan pastikan komponen **Tcl/Tk and IDLE** dipilih. Tkinter biasanya disertakan bersama Python dan tidak dipasang melalui `pip`.

### GUI terbuka tetapi menampilkan error database

Pastikan layanan PostgreSQL aktif, database sudah dibuat, dan file `.env` di folder utama berisi `DATABASE_URL` yang sesuai dengan kredensial, port, serta nama database lokal. Setelah konfigurasi siap, jalankan seed satu kali:

```powershell
python -m database.seed
```

## Menjalankan Pengujian

Jalankan seluruh pengujian dengan unittest discovery:

```powershell
python -m unittest discover -s tests -v
```

Pengujian yang berhubungan dengan database memerlukan:

- PostgreSQL aktif.
- Database pada `DATABASE_URL` tersedia.
- Pengguna database memiliki akses untuk membuat dan mengubah tabel.

## Struktur Utama

```text
main.py                     # Entry point GUI/CLI
config/                     # Konfigurasi path dan environment
database/                   # Koneksi, skema, dan data awal
repositories/               # Akses dan operasi data PostgreSQL
modules/                    # EOQ, Safety Stock, ROP, forecasting, laporan
services/                   # Layanan impor, ekspor, dan inventaris
gui/                        # Antarmuka desktop Tkinter
storage/imports/            # File CSV untuk impor
storage/exports/backups/    # Cadangan CSV
storage/exports/reports/     # Laporan CSV
output/reports/             # Laporan teks
output/charts/              # Grafik hasil laporan
tests/                      # Pengujian unittest
```

## Fitur Utama

- Dashboard stok dan penjualan.
- CRUD produk dan pemasok.
- Transaksi barang masuk dan keluar.
- Pencatatan penjualan dengan pembaruan stok.
- Perhitungan EOQ, Safety Stock, dan Reorder Point.
- Moving Average dan Exponential Smoothing.
- Laporan inventaris dan grafik stok.
- Template serta impor/ekspor CSV melalui Pandas.

## Lokasi File Hasil

- Template CSV: `storage/imports/`
- Cadangan dan laporan ekspor: `storage/exports/`
- Laporan teks: `output/reports/`
- Grafik: `output/charts/`
