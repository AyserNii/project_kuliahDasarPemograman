# SmartStock

SmartStock adalah aplikasi CLI berbasis Python untuk membantu pemilik UMKM
mengelola dan menganalisis persediaan barang. Fondasi awal ini menyiapkan
arsitektur modular dan penyimpanan CSV; fitur perhitungan akan dikembangkan
bertahap.

## Persyaratan

- Python 3.10 atau lebih baru
- pip

## Instalasi

Jalankan dari folder project:

```bash
python -m pip install -r requirements.txt
```

## Menjalankan aplikasi

```bash
python main.py
```

Pilih `0` untuk keluar. Menu analisis masih berupa kerangka pada tahap ini.

## Menjalankan pengujian

```bash
python -m unittest discover -s tests -v
```

## Struktur project

```text
SmartStock/
├── main.py
├── requirements.txt
├── README.md
├── config/
│   └── settings.py
├── modules/
│   ├── __init__.py
│   ├── inventory.py
│   ├── forecasting.py
│   ├── analysis.py
│   ├── validation.py
│   └── report.py
├── database/
│   ├── products.csv
│   └── history.csv
├── output/
│   ├── reports/
│   └── charts/
└── tests/
    ├── __init__.py
    ├── test_inventory.py
    └── test_validation.py
```

## Tanggung jawab modul

- `main.py`: entry point dan menu CLI.
- `config/settings.py`: konfigurasi, skema kolom CSV, dan lokasi folder/file.
- `modules/inventory.py`: kerangka perhitungan persediaan (EOQ, safety stock,
  dan reorder point).
- `modules/forecasting.py`: kerangka analisis dan prediksi permintaan.
- `modules/analysis.py`: kerangka analisis biaya persediaan.
- `modules/validation.py`: validasi teks, angka, dan record produk.
- `modules/report.py`: penyimpanan riwayat analisis dan persiapan folder output.
- `database/`: data master produk dan riwayat dalam format CSV.
- `output/reports/` dan `output/charts/`: lokasi keluaran laporan dan grafik.
- `tests/`: pengujian menggunakan `unittest`.

## Dependency

Dependency awal yang dicantumkan di `requirements.txt` adalah pandas,
matplotlib, dan rich. Kerangka CLI saat ini menggunakan standard library
sehingga dependency tersebut belum diimpor oleh aplikasi.
