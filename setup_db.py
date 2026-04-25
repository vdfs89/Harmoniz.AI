"""Utility script to bootstrap chat_history table on Render Postgres."""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Render External Connection String – override via .env or secrets when needed
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://harmoniz_ai_user:c3TDAxDpLnVuEP20v407DsTWLJ9TCeoA@"
    "dpg-d7maaf0k1i2s7391gs2g-a.ohio-postgres.render.com/harmoniz_ai",
)


def create_table() -> None:
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                user_prompt TEXT,
                ai_answer TEXT,
                mode TEXT
            );
            """
        )

        conn.commit()
        print("✅ Tabela 'chat_history' criada com sucesso no Render!")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Erro: {exc}")
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    create_table()
