# bot/handlers/admin.py

import logging
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_one, fetch_all, execute

logger = logging.getLogger(__name__)


# ============================================================
# UTILS
# ============================================================

def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def _unauthorized(update: Update):
    await update.message.reply_text("❌ Unauthorized")


# ============================================================
# /stats — BOT STATISTICS
# ============================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not _is_admin(user.id):
        await _unauthorized(update)
        return

    total_users = await fetch_one(
        "SELECT COUNT(*) AS count FROM users"
    )

    vip_users = await fetch_one(
        """
        SELECT COUNT(*) AS count
        FROM users
        WHERE vip_until IS NOT NULL
          AND vip_until > NOW()
        """
    )

    await update.message.reply_text(
        f"📊 *AnonyLink Stats*\n\n"
        f"👥 Total users: {total_users['count']}\n"
        f"⭐ Active VIP users: {vip_users['count']}",
        parse_mode="Markdown",
    )


# ============================================================
# /users — LAST 10 USERS
# ============================================================

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not _is_admin(user.id):
        await _unauthorized(update)
        return

    rows = await fetch_all(
        """
        SELECT user_id, created_at, trials_left, vip_until
        FROM users
        ORDER BY created_at DESC
        LIMIT 10
        """
    )

    if not rows:
        await update.message.reply_text("No users found.")
        return

    now = datetime.now(timezone.utc)

    lines = ["👥 *Last 10 Users:*"]
    for r in rows:
        vip = "✅" if r["vip_until"] and r["vip_until"] > now else "❌"
        lines.append(
            f"- `{r['user_id']}` | Trials: {r['trials_left']} | VIP: {vip}"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


# ============================================================
# /grantvip <user_id> <days> — ADMIN ONLY
# ============================================================

async def grantvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = update.effective_user

    if not _is_admin(admin.id):
        await _unauthorized(update)
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage:\n/grantvip <user_id> <days>\n\n"
            "Example:\n/grantvip 659916146 365"
        )
        return

    try:
        target_user_id = int(context.args[0])
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ user_id and days must be numbers")
        return

    now = datetime.now(timezone.utc)

    # 🔍 Fetch existing VIP if user exists
    row = await fetch_one(
        "SELECT vip_until FROM users WHERE user_id = $1",
        target_user_id,
    )

    current_vip_until = row["vip_until"] if row and row["vip_until"] else None

    if current_vip_until and current_vip_until > now:
        new_vip_until = current_vip_until + timedelta(days=days)
    else:
        new_vip_until = now + timedelta(days=days)

    # ✅ UPSERT USER + VIP
    await execute(
        """
        INSERT INTO users (user_id, trials_left, vip_until)
        VALUES ($1, 0, $2)
        ON CONFLICT (user_id)
        DO UPDATE SET vip_until = EXCLUDED.vip_until
        """,
        target_user_id,
        new_vip_until,
    )

    logger.info(
        f"ADMIN VIP GRANT | admin={admin.id} | user={target_user_id} | until={new_vip_until}"
    )

    await update.message.reply_text(
        f"⭐ *VIP Granted Successfully*\n\n"
        f"User: `{target_user_id}`\n"
        f"Valid until: {new_vip_until.strftime('%Y-%m-%d %H:%M UTC')}",
        parse_mode="Markdown",
    )
