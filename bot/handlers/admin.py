# bot/handlers/admin.py
# Admin commands (stats, users, grantvip)

import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db

logger = logging.getLogger(__name__)


# ============================================================
# UTILS
# ============================================================

def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def _unauthorized(update: Update):
    if update.message:
        await update.message.reply_text("❌ Unauthorized")


# ============================================================
# /stats — BOT STATISTICS
# ============================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    if not _is_admin(user.id):
        await _unauthorized(update)
        return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM users
                WHERE vip_until IS NOT NULL
                  AND vip_until > NOW()
                """
            )
            vip_users = cur.fetchone()[0]
    finally:
        conn.close()

    await update.message.reply_text(
        "📊 *TrueMatch Stats*\n\n"
        f"👥 Total users: *{total_users}*\n"
        f"⭐ Active VIP users: *{vip_users}*",
        parse_mode="Markdown",
    )


# ============================================================
# /users — LAST 10 USERS
# ============================================================

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    if not _is_admin(user.id):
        await _unauthorized(update)
        return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, created_at, trials_left, vip_until
                FROM users
                ORDER BY created_at DESC
                LIMIT 10
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        await update.message.reply_text("No users found.")
        return

    now = datetime.now(timezone.utc)

    lines = ["👥 *Last 10 Users:*"]
    for r in rows:
        vip_active = r["vip_until"] and r["vip_until"] > now
        vip_icon = "✅" if vip_active else "❌"
        lines.append(
            f"- `{r['user_id']}` | Trials: {r['trials_left']} | VIP: {vip_icon}"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


# ============================================================
# /grantvip <user_id> <days>
# ============================================================

async def grantvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /grantvip <user_id> <days>"
        )
        return

    try:
        target_user_id = str(context.args[0])   # ✅ TEXT, not int
        days = int(context.args[1])
        if days <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid arguments.\nUsage: /grantvip <user_id> <days>"
        )
        return

    conn = get_db()
    with conn.cursor() as cur:
        # Ensure user exists
        cur.execute(
            """
            INSERT INTO users (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (target_user_id,),
        )

        # Grant / extend VIP
        cur.execute(
            """
            UPDATE users
            SET vip_until = GREATEST(
                COALESCE(vip_until, NOW()),
                NOW()
            ) + (%s || ' days')::INTERVAL
            WHERE user_id = %s
            RETURNING vip_until
            """,
            (days, target_user_id),
        )

        row = cur.fetchone()
        conn.commit()

    conn.close()

    if not row:
        await update.message.reply_text(
            f"❌ Failed to grant VIP to `{target_user_id}`",
            parse_mode="Markdown",
        )
        return

    vip_until = row["vip_until"]

    await update.message.reply_text(
        f"✅ *VIP Granted Successfully!*\n\n"
        f"👤 User ID: `{target_user_id}`\n"
        f"⏳ Valid until: `{vip_until}`",
        parse_mode="Markdown",
    )
