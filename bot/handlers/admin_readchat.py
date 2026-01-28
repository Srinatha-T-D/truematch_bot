# bot/handlers/admin_readchat.py
# Admin-only chat session export (METADATA ONLY)

import io
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.db import get_db
from bot.core.audit import log_admin_action

AUTO_DELETE_SECONDS = 900  # 15 minutes


async def readchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety
    if not update.message:
        return

    admin_id = update.effective_user.id

    # ── SECURITY ─────────────────────────────
    if admin_id not in ADMIN_IDS:
        return

    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ Admin commands only in private chat.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/readchat <session_id>\n\n"
            "Note: Message contents are not stored.\n"
            "This command exports session metadata only."
        )
        return

    session_id = context.args[0]

    # ── FETCH SESSION ────────────────────────
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

    user_a, user_b, started_at, ended_at = row

    duration = (
        int((ended_at - started_at).total_seconds())
        if ended_at
        else "ACTIVE"
    )

    # ── CREATE EXPORT ────────────────────────
    output = io.StringIO()
    output.write("session_id,user_a,user_b,started_at,ended_at,duration\n")
    output.write(
        f"{session_id},{user_a},{user_b},"
        f"{started_at},{ended_at or 'ACTIVE'},{duration}\n"
    )
    output.seek(0)

    sent_doc = await update.message.reply_document(
        document=output.getvalue().encode(),
        filename=f"readchat_{session_id}.csv",
        caption=(
            "📂 *Chat Session Export (Metadata Only)*\n\n"
            f"Session: `{session_id}`\n"
            f"User A: `{user_a}`\n"
            f"User B: `{user_b}`\n"
            f"Started: {started_at:%Y-%m-%d %H:%M UTC}\n"
            f"Ended: {ended_at:%Y-%m-%d %H:%M UTC}" if ended_at else "Ended: ACTIVE\n"
            f"Duration: {duration}\n\n"
            "⛔ Message contents are not stored.\n"
            "🕒 Auto-delete in 15 minutes."
        ),
        parse_mode="Markdown",
        protect_content=True,
    )

    # ── AUDIT ────────────────────────────────
    try:
        await log_admin_action(
            admin_id=admin_id,
            action="READ_CHAT_METADATA",
            metadata={
                "session_id": session_id,
                "user_a": str(user_a),
                "user_b": str(user_b),
                "duration": duration,
            },
        )
    except Exception:
        pass

    # ── AUTO DELETE ──────────────────────────
    async def cleanup():
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        try:
            await sent_doc.delete()
        except Exception:
            pass

    asyncio.create_task(cleanup())


readchat_handler = CommandHandler("readchat", readchat)
