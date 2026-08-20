from aiogram.types import Message


async def build_context(message: Message) -> dict:
    chat = message.chat
    user = message.from_user

    context = {
        "platform": "telegram",

        "chat": {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "username": chat.username,
        },

        "user": {
            "id": user.id,
            "name": user.full_name,
            "username": user.username,
        },

        "message": {
            "id": message.message_id,
            "text": message.text,
        },

        "reply": None,
    }

    if message.reply_to_message:
        replied = message.reply_to_message
        reply_user = replied.from_user

        context["reply"] = {
            "message_id": replied.message_id,
            "text": replied.text,
            "user": None,
        }

        if reply_user:
            context["reply"]["user"] = {
                "id": reply_user.id,
                "name": reply_user.full_name,
                "username": reply_user.username,
            }

    return context
