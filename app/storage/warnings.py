import time

from app.storage.database import get_db

WARN_EXPIRY = 86400  # 24 hours


async def add_warning(
    chat_id: int, user_id: int, reason: str = None
) -> int:
    """Add a warning and return total count (last 24 h)."""
    db = await get_db()
    try:
        cutoff = time.time() - WARN_EXPIRY
        await db.execute(
            "DELETE FROM warnings "
            "WHERE chat_id = ? AND user_id = ? AND timestamp < ?",
            (chat_id, user_id, cutoff),
        )
        await db.execute(
            "INSERT INTO warnings "
            "(chat_id, user_id, reason, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (chat_id, user_id, reason, time.time()),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT COUNT(*) FROM warnings "
            "WHERE chat_id = ? AND user_id = ? AND timestamp >= ?",
            (chat_id, user_id, cutoff),
        )
        row = await cursor.fetchone()
        return row[0] if row else 1
    finally:
        await db.close()


async def get_count(chat_id: int, user_id: int) -> int:
    db = await get_db()
    try:
        cutoff = time.time() - WARN_EXPIRY
        cursor = await db.execute(
            "SELECT COUNT(*) FROM warnings "
            "WHERE chat_id = ? AND user_id = ? AND timestamp >= ?",
            (chat_id, user_id, cutoff),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0
    finally:
        await db.close()


async def reset(chat_id: int, user_id: int):
    """Reset all warnings for a user in a chat."""
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )
        await db.commit()
    finally:
        await db.close()
