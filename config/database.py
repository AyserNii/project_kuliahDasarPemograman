import os
from pathlib import Path
from dotenv import load_dotenv

BERKAS_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BERKAS_ENV)

URL_BASIS_DATA = os.getenv("DATABASE_URL")

def ambil_url_basis_data() -> str:
    """Mengambil koneksi string database dari environment variable."""
    url_basis_data = os.getenv("DATABASE_URL")
    if not url_basis_data:
        raise RuntimeError("DATABASE_URL belum diatur di file .env")
    return url_basis_data
