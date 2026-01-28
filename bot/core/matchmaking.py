# bot/core/matchmaking.py
# Frozen matchmaking engine — DO NOT MIX LOGIC HERE

import logging
import asyncio
from typing import Dict, Tuple, Optional

from bot.core.redis import get_redis
from bot.utils.keyboards import disconnect_keyboard
from bot.core.chat_logger import create_chat_session, end_chat_session
from bot.core.db import get_db

logger = logging.getLogger(__name__)

# user_id -> (partner_user_id, partner_chat_id, session_id)
ACTIVE_CHATS: Dict[str, Tuple[str, int, str]] = {}

QUEUE_KEY = "matchmaking:queue"


# =========================
# INTERNAL HELPERS
# =========================

def _uid(user_id) -> str:
    """Normalize user_id to TEXT (DB-safe)"""
    return str(user_id)


# =========================
# QUEUE HELPERS
# =========================

async def enqueue(user_id: int, chat_id: int):
    redis = await get_redis()
    await redis.sadd(QUEUE_KEY, f"{_uid(user_id)}:{chat_id}")


async def dequeue(user_id: int):
    redis = await get_redis()
    uid = _uid(user_id)

    members = await redis.smembers(QUEUE_KEY)
    for m in members:
        mid = m.decode() if isinstance(m, bytes) else m
        if mid.split(":")[0] == uid:
            await redis.srem(QUEUE_KEY, m)
            return


async def _queue_members(exclude_user: int):
    redis = await get_redis()
    exclude_uid = _uid(exclude_user)

    members = await redis.smembers(QUEUE_KEY)
    result = []

    for m in members:
        mid = m.decode() if isinstance(m, bytes) else m
        uid, chat = mid.split(":")
        if uid != exclude_uid:
            result.append((uid, int(chat)))

    return result


# =========================
# MATCH FINDERS
# =========================

def _fetch_user(user_id: int) -> Optional[dict]:
    user_id = _uid(user_id)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE user_id=%s",
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None

            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))
    finally:
        conn.close()


async def find_strict_match(user: dict) -> Optional[Tuple[str, int]]:
    """
    Gender <-> looking_for ONLY
    """
    for partner_id, partner_chat in await _queue_members(user["user_id"]):
        partner = _fetch_user(partner_id)
        if not partner:
            continue

        if (
            partner["gender"] == user["looking_for"]
            and partner["looking_for"] == user["gender"]
        ):
            return partner_id, partner_chat

    return None


async def find_vip_match(user: dict) -> Optional[Tuple[str, int]]:
    """
    VIP match with SOFT filters (gender NEVER relaxed)
    """
    candidates = []

    for partner_id, partner_chat in await _queue_members(user["user_id"]):
        partner = _fetch_user(partner_id)
        if not partner:
            continue

        # HARD RULE
        if partner["gender"] != user["looking_for"]:
            continue

        candidates.append((partner, partner_chat))

    # Exact VIP preferences
    for partner, chat_id in candidates:
        if user.get("verified_only") and not partner.get("is_verified"):
            continue

        if user.get("age_min") and partner.get("age") is not None:
            if partner["age"] < user["age_min"]:
                continue

        if user.get("age_max") and partner.get("age") is not None:
            if partner["age"] > user["age_max"]:
                continue

        if user.get("state") and partner.get("state"):
            if user["state"] != partner["state"]:
                continue

        if user.get("language") and partner.get("language"):
            if user["language"] != partner["language"]:
                continue

        return partner["user_id"], chat_id

    # Fallback: gender only
    if candidates:
        partner, chat_id = candidates[0]
        return partner["user_id"], chat_id

    return None


# =========================
# PUBLIC ENTRY POINT
# =========================

async def try_match(user_id: int, chat_id: int) -> bool:
    """
    Returns True if matched, False if consent required
    """
    uid = _uid(user_id)

    if uid in ACTIVE_CHATS:
        return True

    user = _fetch_user(uid)
    if not user:
        return False

    await enqueue(uid, chat_id)

    # 🔐 VIP USERS
    if user.get("is_vip"):
        match = await find_vip_match(user)
        if match:
            partner_id, partner_chat = match
            await _connect(uid, chat_id, partner_id, partner_chat)
            return True
        return False

    # 🆓 FREE USERS
    match = await find_strict_match(user)
    if match:
        partner_id, partner_chat = match
        await _connect(uid, chat_id, partner_id, partner_chat)
        return True

    return False


# =========================
# MATCH EXECUTION
# =========================

async def _connect(
    user_id: str,
    chat_id: int,
    partner_id: str,
    partner_chat_id: int,
):
    await dequeue(user_id)
    await dequeue(partner_id)

    session_id = await create_chat_session(user_id, partner_id)

    ACTIVE_CHATS[user_id] = (partner_id, partner_chat_id, session_id)
    ACTIVE_CHATS[partner_id] = (user_id, chat_id, session_id)

    text = (
        "🎉 *You are now connected anonymously!*\n\n"
        "💬 Say hi and start chatting\n"
        "❌ Tap Disconnect to end the chat\n"
        "🚩 You can report after the chat ends"
    )

    from bot.app import bot
    await asyncio.gather(
        *[
            bot.send_message(
                chat_id=cid,
                text=text,
                reply_markup=disconnect_keyboard(),
                parse_mode="Markdown",
            )
            for cid in (chat_id, partner_chat_id)
        ]
    )


# =========================
# ACTIVE CHAT HELPERS
# =========================

def get_partner(user_id: int):
    return ACTIVE_CHATS.get(_uid(user_id))


def disconnect_users(user_id: int):
    uid = _uid(user_id)

    chat = ACTIVE_CHATS.pop(uid, None)
    if not chat:
        return

    partner_id, _, session_id = chat
    ACTIVE_CHATS.pop(partner_id, None)

    asyncio.create_task(end_chat_session(session_id))
