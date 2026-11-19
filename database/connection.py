import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def buat_koneksi():
    berkas_env = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(berkas_env)

    url_basis_data = os.getenv("DATABASE_URL")
    if not url_basis_data:
        raise RuntimeError(
            "DATABASE_URL belum diatur. Isi variabel tersebut di file .env."
        )

    return psycopg.connect(url_basis_data)