import statistics
from typing import Dict, List, Optional
import pandas as pd


def rata_rata_bergerak(data: List[float], ukuran_jendela: int = 3) -> float:
    """
    Menghitung Moving Average untuk peramalan permintaan periode berikutnya.
    """
    if not data:
        return 0.0
    if ukuran_jendela <= 0:
        raise ValueError("Ukuran jendela harus lebih besar dari 0")

    jendela = [float(nilai) for nilai in data[-ukuran_jendela:]]
    return round(sum(jendela) / len(jendela), 2)


def peramalan_rata_rata_bergerak_pandas(data: List[float], ukuran_jendela: int = 3) -> List[Optional[float]]:
    """
    Menghitung deret Moving Average secara menyeluruh menggunakan Pandas Series.
    (Materi Penggunaan Pandas DataFrame/Series untuk Analisis Data)
    """
    if not data:
        return []
    elemen = pd.Series([float(nilai) for nilai in data])
    hasil_bergulir = elemen.rolling(window=ukuran_jendela).mean()
    return [
        round(nilai, 2) if not pd.isna(nilai) else None
        for nilai in hasil_bergulir
    ]


def rata_rata_bergerak_tertimbang(data: List[float], bobot: Optional[List[float]] = None) -> float:
    """
    Menghitung Weighted Moving Average (WMA).
    Bobot nilai_default adalah bertingkat dari 1 s.d. n.
    """
    if not data:
        return 0.0

    jumlah = len(data)
    if bobot is None:
        bobot = list(range(1, jumlah + 1))

    if len(bobot) != jumlah:
        raise ValueError("Jumlah bobot harus sama dengan jumlah data")

    total_bobot = sum(bobot)
    if total_bobot == 0:
        raise ValueError("Total bobot tidak boleh 0")

    jumlah_tertimbang = sum(
        float(nilai) * float(bobot_data)
        for nilai, bobot_data in zip(data, bobot)
    )
    return round(jumlah_tertimbang / total_bobot, 2)


def pemulusan_eksponensial(data: List[float], alfa: float = 0.3) -> float:
    """
    Menghitung Single Exponential Smoothing (SES).
    - alfa: faktor pembobotan (0 < alfa <= 1)
    """
    if not data:
        return 0.0
    if not (0 < alfa <= 1):
        raise ValueError("Alpha harus berada di antara 0 dan 1 (0 < alfa <= 1)")

    peramalan = float(data[0])
    for nilai_aktual in data[1:]:
        peramalan = (alfa * float(nilai_aktual)) + ((1 - alfa) * peramalan)

    return round(peramalan, 2)


def hitung_statistik_permintaan(kuantitas_harian: List[float]) -> Dict[str, float]:
    """
    Menghitung metrik permintaan dari data kuantitas harian:
    - Rata-rata permintaan harian (rata_rata_permintaan_harian)
    - Standar deviasi harian (simpangan_baku_permintaan_harian)
    - Estimasi permintaan tahunan (permintaan_tahunan)
    """
    if not kuantitas_harian:
        return {
            "rata_rata_permintaan_harian": 0.0,
            "simpangan_baku_permintaan_harian": 0.0,
            "permintaan_tahunan": 0.0,
        }

    daftar_angka = [float(nilai) for nilai in kuantitas_harian]
    rata_rata = sum(daftar_angka) / len(daftar_angka)

    if len(daftar_angka) > 1:
        simpangan_baku = statistics.stdev(daftar_angka)
    else:
        simpangan_baku = 0.0

    tahunan = rata_rata * 365.0

    return {
        "rata_rata_permintaan_harian": round(rata_rata, 2),
        "simpangan_baku_permintaan_harian": round(simpangan_baku, 2),
        "permintaan_tahunan": round(tahunan, 2),
        "rata_rata_harian": round(rata_rata, 2),
        "standar_deviasi_harian": round(simpangan_baku, 2),
        "proyeksi_tahunan": round(tahunan, 2),
        "average_daily_demand": round(rata_rata, 2),
        "daily_demand_stddev": round(simpangan_baku, 2),
        "annual_demand": round(tahunan, 2),
    }


# Alias kompatibilitas
moving_average = rata_rata_bergerak
weighted_moving_average = rata_rata_bergerak_tertimbang
exponential_smoothing = pemulusan_eksponensial
hitung_rata_rata_bergerak = rata_rata_bergerak
peramalan_eksponensial = pemulusan_eksponensial
calculate_demand_statistics = hitung_statistik_permintaan
pandas_rolling_forecast = peramalan_rata_rata_bergerak_pandas
