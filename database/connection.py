import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_connection():
    env_file = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_file)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL belum diatur. Isi variabel tersebut di file .env."
        )

    return psycopg.connect(database_url)