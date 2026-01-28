# bot/core/db.py
# Single authoritative DB access layer
# Aligned with current users table schema
import logging
logging.warning("✅ USING bot/core/db.py (psycopg2)")

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from bot.config.settings import DATABASE_URL


# =========================
# CONNECTION
# =========================

def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

# =========================
# USER CREATION / FETCH
# =========================

def ensure_user(user_id: str, username: str | None = None):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (user_id, username)
            )
        conn.commit()
    finally:
        conn.close()


def get_user(user_id: str):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE user_id = %s",
                (user_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


# =========================
# BAN SYSTEM (AUTHORITATIVE)
# =========================

def set_hard_ban(user_id: str, status: bool):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET is_banned = %s
                WHERE user_id = %s
                """,
                (status, user_id)
            )
        conn.commit()
    finally:
        conn.close()


def is_hard_banned(user_id: str) -> bool:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT is_banned FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            return bool(row and row["is_banned"])
    finally:
        conn.close()


def is_shadow_banned(user_id: str) -> bool:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT shadow_banned FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            return bool(row and row["shadow_banned"])
    finally:
        conn.close()


# =========================
# TRIAL SYSTEM (trials_left)
# =========================

def get_trials_left(user_id: str) -> int:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT trials_left FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            return int(row["trials_left"]) if row else 0
    finally:
        conn.close()


def consume_trial(user_id: str) -> bool:
    """
    Decrease trials_left by 1 if available.
    Returns True if consumed, False if none left.
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET trials_left = trials_left - 1
                WHERE user_id = %s
                  AND trials_left > 0
                RETURNING trials_left
                """,
                (user_id,)
            )
            row = cur.fetchone()
        conn.commit()
        return row is not None
    finally:
        conn.close()


# =========================
# VIP SYSTEM (vip_until ONLY)
# =========================

def set_vip_until(user_id: str, vip_until: datetime):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET vip_until = %s
                WHERE user_id = %s
                """,
                (vip_until, user_id)
            )
        conn.commit()
    finally:
        conn.close()


def is_vip(user_id: str) -> bool:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT vip_until
                FROM users
                WHERE user_id = %s
                  AND vip_until IS NOT NULL
                  AND vip_until > NOW()
                """,
                (user_id,)
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


# =========================
# REPORT SYSTEM
# =========================

def increment_report(user_id: str) -> int:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET report_count = report_count + 1
                WHERE user_id = %s
                RETURNING report_count
                """,
                (user_id,)
            )
            count = cur.fetchone()["report_count"]
        conn.commit()
        return count
    finally:
        conn.close()


def get_report_count(user_id: str) -> int:
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT report_count FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            return row["report_count"] if row else 0
    finally:
        conn.close()


# =========================
# ACTIVITY
# =========================

def update_last_active(user_id: str):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET last_active = NOW()
                WHERE user_id = %s
                """,
                (user_id,)
            )
        conn.commit()
    finally:
        conn.close()
