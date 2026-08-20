import time

from app.storage.database import get_db

MAX_HISTORY = 20


async def add_message(
    chat_id: int,
    role: str,
    content: str,
    user_id: int = None,
    user_name: str = None,
):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO chat_history "
            "(chat_id, user_id, user_name, role, content, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, user_id, user_name, role, content, time.time()),
        )
        # Keep only the last MAX_HISTORY messages per chat
        await db.execute(
            "DELETE FROM chat_history "
            "WHERE chat_id = ? AND id NOT IN ("
            "  SELECT id FROM chat_history "
            "  WHERE chat_id = ? "
            "  ORDER BY timestamp DESC LIMIT ?"
            ")",
            (chat_id, chat_id, MAX_HISTORY),
        )
        await db.commit()
    finally:
        await db.close()


async def get_history(chat_id: int, limit: int = MAX_HISTORY) -> list:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT role, content, user_name "
            "FROM chat_history "
            "WHERE chat_id = ? "
            "ORDER BY timestamp ASC LIMIT ?",
            (chat_id, limit),
        )
        rows = await cursor.fetchall()
        messages = []
        for role, content, user_name in rows:
            if role == "user" and user_name:
                content = f"[{user_name}]: {content}"
            messages.append({"role": role, "content": content})
        return messages
    finally:
        await db.close()


async def clear_history(chat_id: int):
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM chat_history WHERE chat_id = ?",
            (chat_id,),
        )
        await db.commit()
    finally:
        await db.close()
