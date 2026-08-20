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
            "INSERT INTO group_settings (chat_id, strict_mode) "
            "VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET strict_mode = ?",
            (chat_id, int(enabled), int(enabled)),
        )
        await db.commit()
    finally:
        await db.close()


async def get_welcome_msg(chat_id: int) -> str:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT welcome_msg FROM group_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row and row[0] else None
    finally:
        await db.close()


async def set_welcome_msg(chat_id: int, msg: str):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO group_settings (chat_id, welcome_msg) "
            "VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET welcome_msg = ?",
            (chat_id, msg, msg),
        )
        await db.commit()
    finally:
        await db.close()
