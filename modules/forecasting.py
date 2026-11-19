import math
import statistics
from typing import Dict, List, Optional
import pandas as pd


def moving_average(data: List[float], window_size: int = 3) -> float:
    """
    Menghitung Moving Average untuk peramalan permintaan periode berikutnya.
    """
    if not data:
        return 0.0
    if window_size <= 0:
        raise ValueError("Ukuran window harus lebih besar dari 0")

    window = [float(x) for x in data[-window_size:]]
    return round(sum(window) / len(window), 2)


def pandas_rolling_forecast(data: List[float], window_size: int = 3) -> List[Optional[float]]:
    """
    Menghitung deret Moving Average secara menyeluruh menggunakan Pandas Series.
    (Materi Penggunaan Pandas DataFrame/Series untuk Analisis Data)
    """
    if not data:
        return []
    s = pd.Series([float(x) for x in data])
    rolling = s.rolling(window=window_size).mean()
    return [round(val, 2) if not pd.isna(val) else None for val in rolling]


def weighted_moving_average(data: List[float], weights: Optional[List[float]] = None) -> float:
    """
    Menghitung Weighted Moving Average (WMA).
    Bobot default adalah bertingkat dari 1 s.d. n.
    """
    if not data:
        return 0.0

    n = len(data)
    if weights is None:
        weights = list(range(1, n + 1))

    if len(weights) != n:
        raise ValueError("Jumlah bobot harus sama dengan jumlah data")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total bobot tidak boleh 0")

    weighted_sum = sum(float(d) * float(w) for d, w in zip(data, weights))
    return round(weighted_sum / total_weight, 2)


def exponential_smoothing(data: List[float], alpha: float = 0.3) -> float:
    """
    Menghitung Single Exponential Smoothing (SES).
    - alpha: faktor pembobotan (0 < alpha <= 1)
    """
    if not data:
        return 0.0
    if not (0 < alpha <= 1):
        raise ValueError("Alpha harus berada di antara 0 dan 1 (0 < alpha <= 1)")

    forecast = float(data[0])
    for actual in data[1:]:
        forecast = (alpha * float(actual)) + ((1 - alpha) * forecast)

    return round(forecast, 2)


def calculate_demand_statistics(daily_quantities: List[float]) -> Dict[str, float]:
    """
    Menghitung metrik permintaan dari data kuantitas harian:
    - Rata-rata permintaan harian (average_daily_demand)
    - Standar deviasi harian (daily_demand_stddev)
    - Estimasi permintaan tahunan (annual_demand)
    """
    if not daily_quantities:
        return {
            "average_daily_demand": 0.0,
            "daily_demand_stddev": 0.0,
            "annual_demand": 0.0,
        }

    floats = [float(x) for x in daily_quantities]
    avg = sum(floats) / len(floats)

    if len(floats) > 1:
        stddev = statistics.stdev(floats)
    else:
        stddev = 0.0

    annual = avg * 365.0

    return {
        "average_daily_demand": round(avg, 2),
        "daily_demand_stddev": round(stddev, 2),
        "annual_demand": round(annual, 2),
    }
