# bot/core/db.py

import psycopg2
from bot.config.settings import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False

# =========================
# USER STATUS
# =========================

def set_banned(user_id: int, status: bool):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET banned=%s WHERE telegram_id=%s",
            (status, user_id)
        )
        conn.commit()

def is_banned(user_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT banned FROM users WHERE telegram_id=%s",
            (user_id,)
        )
        row = cur.fetchone()
        return row[0] if row else False

# =========================
# REPORT SYSTEM
# =========================

def increment_report(user_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE users
            SET report_count = report_count + 1
            WHERE telegram_id=%s
            RETURNING report_count
            """,
            (user_id,)
        )
        count = cur.fetchone()[0]
        conn.commit()
        return count
