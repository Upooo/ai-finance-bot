import time

from app.storage.database import get_db


async def get_strict_mode(chat_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT strict_mode FROM group_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
    finally:
        await db.close()


async def set_strict_mode(chat_id: int, enabled: bool):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO group_settings (chat_id, strict_mode)
               VALUES (?, ?)
               ON CONFLICT(chat_id)
               DO UPDATE SET strict_mode = excluded.strict_mode""",
            (chat_id, int(enabled)),
        )
        await db.commit()
    finally:
        await db.close()


async def get_chat_mode(chat_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT chat_mode FROM group_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
    finally:
        await db.close()


async def set_chat_mode(chat_id: int, enabled: bool):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO group_settings (chat_id, chat_mode)
               VALUES (?, ?)
               ON CONFLICT(chat_id)
               DO UPDATE SET chat_mode = excluded.chat_mode""",
            (chat_id, int(enabled)),
        )
        await db.commit()
    finally:
        await db.close()


async def get_nimbrung_mode(chat_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT nimbrung_mode FROM group_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
    finally:
        await db.close()


async def set_nimbrung_mode(chat_id: int, enabled: bool):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO group_settings (chat_id, nimbrung_mode)
               VALUES (?, ?)
               ON CONFLICT(chat_id)
               DO UPDATE SET nimbrung_mode = excluded.nimbrung_mode""",
            (chat_id, int(enabled)),
        )
        await db.commit()
    finally:
        await db.close()


# -- Active conversation tracking --

CONVERSATION_TIMEOUT = 300  # 5 minutes


async def mark_active(chat_id: int, topic_hint: str = ""):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO active_conversations (chat_id, last_active, topic_hint)
               VALUES (?, ?, ?)
               ON CONFLICT(chat_id)
               DO UPDATE SET last_active = excluded.last_active,
                            topic_hint = excluded.topic_hint""",
            (chat_id, time.time(), topic_hint),
        )
        await db.commit()
    finally:
        await db.close()


async def is_conversation_active(chat_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT last_active FROM active_conversations WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return False
        return (time.time() - row[0]) < CONVERSATION_TIMEOUT
    finally:
        await db.close()


async def end_conversation(chat_id: int):
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM active_conversations WHERE chat_id = ?",
            (chat_id,),
        )
        await db.commit()
    finally:
        await db.close()
