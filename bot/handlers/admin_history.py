from telegram import Update
from telegram.ext import ContextTypes
from bot.config.settings import ADMIN_IDS
from bot.core.database import fetch_all


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


async def chat_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /chat_history <user_id>")
        return

    user_id = int(context.args[0])

    rows = await fetch_all(
        """
        SELECT id, user_a, user_b, started_at
        FROM chat_sessions
        WHERE user_a = $1 OR user_b = $1
        ORDER BY started_at DESC
        LIMIT 10
        """,
        user_id,
    )

    if not rows:
        await update.message.reply_text("No chat history found.")
        return

    lines = ["📜 *Chat History*"]
    for r in rows:
        other = r["user_b"] if r["user_a"] == user_id else r["user_a"]
        lines.append(f"`{r['id']}` ↔ `{other}` ({r['started_at']:%Y-%m-%d})")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def view_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /view_chat <session_id>")
        return

    session_id = context.args[0]

    rows = await fetch_all(
        """
        SELECT sender_id, message
        FROM chat_messages
        WHERE session_id = $1
        ORDER BY sent_at
        """,
        session_id,
    )

    if not rows:
        await update.message.reply_text("No messages found.")
        return

    text = "\n".join(f"[{r['sender_id']}] {r['message']}" for r in rows[:50])
    await update.message.reply_text(text or "Empty chat")
