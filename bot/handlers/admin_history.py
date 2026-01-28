# bot/handlers/admin_history.py
# Admin chat history & session inspection (metadata only)

from telegram import Update
from telegram.ext import ContextTypes

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# --------------------------------------------------
# /chat_history <user_id>
# --------------------------------------------------
async def chat_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    if not context.args:
        await update.message.reply_text("Usage: /chat_history <user_id>")
        return

    try:
        user_id = str(int(context.args[0]))
    except ValueError:
        await update.message.reply_text("❌ Invalid user_id")
        return

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_a, user_b, started_at, ended_at
                FROM chat_sessions
                WHERE user_a = %s OR user_b = %s
                ORDER BY started_at DESC
                LIMIT 10
                """,
                (user_id, user_id),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        await update.message.reply_text("No chat history found.")
        return

    lines = ["📜 *Chat History (Last 10)*"]
    for r in rows:
        other = r["user_b"] if r["user_a"] == user_id else r["user_a"]
        status = "ENDED" if r["ended_at"] else "ACTIVE"
        lines.append(
            f"`{r['id']}` ↔ `{other}` | {status} | {r['started_at']:%Y-%m-%d}"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        protect_content=True,
    )


# --------------------------------------------------
# /view_chat <session_id>
# (METADATA ONLY – messages are not stored)
# --------------------------------------------------
async def view_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    if not context.args:
        await update.message.reply_text("Usage: /view_chat <session_id>")
        return

    session_id = context.args[0]

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_a, user_b, started_at, ended_at
                FROM chat_sessions
                WHERE id = %s
                """,
                (session_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        await update.message.reply_text("❌ Session not found.")
        return

    duration = (
        int((row["ended_at"] - row["started_at"]).total_seconds())
        if row["ended_at"]
        else "ACTIVE"
    )

    await update.message.reply_text(
        "👁️ *Chat Session Details*\n\n"
        f"Session ID: `{session_id}`\n"
        f"User A: `{row['user_a']}`\n"
        f"User B: `{row['user_b']}`\n"
        f"Started: {row['started_at']:%Y-%m-%d %H:%M UTC}\n"
        f"Ended: {row['ended_at']:%Y-%m-%d %H:%M UTC}"
        if row["ended_at"]
        else "Ended: *ACTIVE*\n"
        f"Duration: {duration}",
        parse_mode="Markdown",
        protect_content=True,
    )
