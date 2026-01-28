# bot/handlers/admin_verification.py
# Admin verification management (schema-safe)

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.db import get_db
from bot.utils.logger import logger


# ===============================
# VERIFY STATS
# ===============================
async def verify_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (WHERE status = 'pending')   AS pending,
                    COUNT(*) FILTER (WHERE status = 'approved')  AS approved,
                    COUNT(*) FILTER (WHERE status = 'rejected')  AS rejected,
                    COUNT(*)                                     AS total
                FROM verification_requests
                """
            )
            row = cur.fetchone() or {}
    finally:
        conn.close()

    await update.message.reply_text(
        "📊 *Verification Stats*\n\n"
        f"⏳ Pending: *{row.get('pending', 0)}*\n"
        f"✅ Approved: *{row.get('approved', 0)}*\n"
        f"❌ Rejected: *{row.get('rejected', 0)}*\n"
        f"📦 Total requests: *{row.get('total', 0)}*",
        parse_mode="Markdown",
    )


# ===============================
# LIST PENDING VERIFICATIONS
# ===============================
async def verify_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM verification_requests
                WHERE status = 'pending'
                """
            )
            total_pending = (cur.fetchone() or {}).get("total", 0)

            cur.execute(
                """
                SELECT
                    user_id,
                    full_name,
                    gender,
                    contact,
                    created_at
                FROM verification_requests
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 10
                """
            )
            rows = cur.fetchall() or []
    finally:
        conn.close()

    if total_pending == 0:
        await update.message.reply_text("✅ No pending verification requests.")
        return

    msg = [
        "🛡️ *Pending Verifications*\n"
        f"📌 Total pending: *{total_pending}*\n"
    ]

    for i, r in enumerate(rows, 1):
        msg.append(
            f"{i}️⃣ *User ID:* `{r['user_id']}`\n"
            f"• *Name:* {r['full_name']}\n"
            f"• *Gender:* {r['gender']}\n"
            f"• *Contact:* {r['contact']}\n"
            f"• *Requested:* {r['created_at'].strftime('%d %b %Y, %I:%M %p')}\n"
        )

    msg.append(
        "\n⚙️ *Admin Actions*\n"
        "`/verify_approve <user_id>`\n"
        "`/verify_reject <user_id> <reason>`"
    )

    await update.message.reply_text("\n".join(msg), parse_mode="Markdown")


# ===============================
# APPROVE VERIFICATION (FIXED)
# ===============================
async def verify_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /verify_approve <user_id>")
        return

    user_id = context.args[0]

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE verification_requests
                SET status = 'approved'
                WHERE user_id = %s
                  AND status = 'pending'
                """,
                (user_id,),
            )

            if cur.rowcount == 0:
                await update.message.reply_text("❌ No pending request found.")
                return

            cur.execute(
                """
                UPDATE users
                SET is_verified = TRUE
                WHERE user_id = %s::text
                """,
                (user_id,),
            )

        conn.commit()
    finally:
        conn.close()

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=(
                "🎉 *Verification Approved!*\n\n"
                "✅ Your account is now *verified*.\n"
                "⭐ VIP users will prefer you.\n\n"
                "Thanks for helping keep the platform safe."
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning("Notify approve failed user=%s err=%s", user_id, e)

    await update.message.reply_text(
        f"✅ User `{user_id}` verified and notified.",
        parse_mode="Markdown",
    )


# ===============================
# REJECT VERIFICATION (FIXED)
# ===============================
async def verify_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage: /verify_reject <user_id> <reason>"
        )
        return

    user_id = context.args[0]
    reason = " ".join(context.args[1:]) or "Not specified"

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE verification_requests
                SET status = 'rejected'
                WHERE user_id = %s
                  AND status = 'pending'
                """,
                (user_id,),
            )

            if cur.rowcount == 0:
                await update.message.reply_text("❌ No pending request found.")
                return

        conn.commit()
    finally:
        conn.close()

    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=(
                "❌ *Verification Rejected*\n\n"
                f"Reason: _{reason}_\n\n"
                "You can re-apply with correct details."
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning("Notify reject failed user=%s err=%s", user_id, e)

    await update.message.reply_text(
        f"❌ User `{user_id}` rejected and notified.",
        parse_mode="Markdown",
    )
