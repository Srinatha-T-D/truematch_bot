# bot/core/database.py

import logging
import asyncpg
from typing import Optional, List

from bot.config.settings import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


# ============================================================
# CONNECTION
# ============================================================

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        logger.info("🔌 Creating PostgreSQL connection pool")
        _pool = await asyncpg.create_pool(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            min_size=1,
            max_size=5,
        )
    return _pool


# ============================================================
# HELPERS (FIXED)
# ============================================================

async def fetch_one(query: str, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetch_all(query: str, *args) -> List[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute(query: str, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(query, *args)
