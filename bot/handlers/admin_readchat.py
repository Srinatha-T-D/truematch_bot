# bot/handlers/admin_readchat.py

import csv
import io
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_all
from bot.core.audit import log_admin_action

AUTO_DELETE_SECONDS = 900  # 15 minutes


def parse_datetime(value: str) -> datetime:
    if "T" in value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    return datetime.strptime(value, "%Y-%m-%d")


async def readchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id

    # ── SECURITY ─────────────────────────────
    if admin_id not in ADMIN_IDS:
        return

    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ Admin commands only in private chat.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/readchat <session_id>\n"
            "/readchat <session_id> user=<id>\n"
            "/readchat <session_id> from=YYYY-MM-DD to=YYYY-MM-DD"
        )
        return

    session_id = context.args[0]
    start_time = None
    end_time = None
    filter_user = None

    for arg in context.args[1:]:
        if arg.startswith("from="):
            start_time = parse_datetime(arg.replace("from=", ""))
        elif arg.startswith("to="):
            end_time = parse_datetime(arg.replace("to=", ""))
        elif arg.startswith("user="):
            filter_user = int(arg.replace("user=", ""))

    # ── QUERY ────────────────────────────────
    query = """
        SELECT sent_at, sender_id, message_type, message, file_id
        FROM chat_messages
        WHERE session_id = $1
    """
    params = [session_id]
    idx = 2

    if filter_user:
        query += f" AND sender_id = ${idx}"
        params.append(filter_user)
        idx += 1

    if start_time:
        query += f" AND sent_at >= ${idx}"
        params.append(start_time)
        idx += 1

    if end_time:
        query += f" AND sent_at <= ${idx}"
        params.append(end_time)
        idx += 1

    query += " ORDER BY sent_at ASC"

    rows = await fetch_all(query, *params)

    if not rows:
        await update.message.reply_text("⚠️ No messages found.")
        return

    # ── CREATE CSV ───────────────────────────
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "sent_at",
        "sender_id",
        "message_type",
        "message",
        "file_id"
    ])

    for r in rows:
        writer.writerow([
            r["sent_at"].strftime("%Y-%m-%d %H:%M:%S"),
            r["sender_id"],
            r["message_type"],
            r["message"] or "",
            r["file_id"] or "",
        ])

    output.seek(0)

    filename = f"readchat_{session_id}.csv"

    sent_doc = await update.message.reply_document(
        document=output.getvalue().encode(),
        filename=filename,
        caption=(
            f"📂 READ-ONLY CHAT EXPORT\n"
            f"Session: {session_id}\n"
            f"Messages: {len(rows)}\n"
            f"User: {filter_user or 'ALL'}\n"
            f"Auto-delete in 15 minutes"
        ),
        protect_content=True
    )

    # ── AUDIT ────────────────────────────────
    await log_admin_action(
        admin_id=admin_id,
        action="READ_CHAT_EXPORT",
        metadata={
            "session_id": session_id,
            "rows": len(rows),
            "user_filter": filter_user,
            "from": start_time.isoformat() if start_time else None,
            "to": end_time.isoformat() if end_time else None,
        }
    )

    # ── AUTO DELETE ──────────────────────────
    async def cleanup():
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        try:
            await sent_doc.delete()
        except:
            pass

    asyncio.create_task(cleanup())


readchat_handler = CommandHandler("readchat", readchat)
