import asyncio
import json
import os
import re
import traceback

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from app.ai.agent import AIAgent
from app.telegram.context import build_context
from app.telegram.triggers import should_respond, clean_trigger, is_dismiss
from app.telegram.typing import TypingManager
from app.telegram.permissions import can_manage

from app.storage.database import init_db
from app.storage.memory import add_message
from app.storage.warnings import (
    add_warning,
    get_count,
    reset,
)
from app.storage.settings import (
    get_strict_mode, set_strict_mode,
    get_chat_mode, set_chat_mode,
    get_nimbrung_mode, set_nimbrung_mode,
    mark_active, is_conversation_active, end_conversation,
)

from app.telegram.management import (
    get_group_info,
    get_group_admins,
    promote_user,
    demote_user,
    ban_user,
    unban_user,
    mute_user,
    unmute_user,
    delete_message,
    create_invite_link,
    pin_message,
    unpin_message,
    set_chat_title,
    set_chat_description,
    get_member_count,
    create_voice_chat,
    end_voice_chat,
    create_poll,
    set_slow_mode,
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

dp = Dispatcher()
ai = AIAgent(GROQ_API_KEY)


# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Helpers
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def sanitize_html(text: str) -> str:
    if not text:
        return ""
    allowed = {'b', 'i', 'u', 's', 'code', 'pre', 'a', 'tg-spoiler', 'blockquote', 'em', 'strong'}
    import re as _re
    def _check(m):
        full = m.group(0)
        tag_match = _re.match(r'</?([a-zA-Z][a-zA-Z0-9-]*)', full)
        if not tag_match:
            return full
        tag = tag_match.group(1).lower()
        if tag in allowed:
            return full
        return ''
    return _re.sub(r'<[^>]+>', _check, text)


async def execute_tool(
    bot: Bot,
    message: Message,
    tool_name: str,
    args: dict,
):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # \u2500\u2500 Read-only tools \u2500\u2500
    if tool_name == "get_group_info":
        return await get_group_info(bot=bot, chat_id=chat_id)
    if tool_name == "get_group_admins":
        return await get_group_admins(bot=bot, chat_id=chat_id)
    if tool_name == "get_member_count":
        return await get_member_count(bot=bot, chat_id=chat_id)

    # \u2500\u2500 Settings tools (bot admin-only) \u2500\u2500
    if tool_name == "toggle_strict_mode":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="toggle_strict_mode",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED. Hanya owner bot dan admin Idol yang bisa."}
        enabled = args.get("enabled", False)
        await set_strict_mode(chat_id, enabled)
        return {"success": True, "strict_mode": enabled}

    if tool_name == "toggle_chat_mode":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="toggle_chat_mode",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED. Hanya owner bot dan admin Idol yang bisa."}
        enabled = args.get("enabled", False)
        await set_chat_mode(chat_id, enabled)
        if not enabled:
            await end_conversation(chat_id)
        return {"success": True, "chat_mode": enabled}

    if tool_name == "toggle_nimbrung":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="toggle_nimbrung",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED. Hanya owner bot dan admin Idol yang bisa."}
        enabled = args.get("enabled", False)
        await set_nimbrung_mode(chat_id, enabled)
        return {"success": True, "nimbrung_mode": enabled}

    # \u2500\u2500 Warning tools \u2500\u2500
    if tool_name == "warn_user":
        target_id = args.get("user_id")
        if not target_id:
            return {"success": False, "error": "Missing user_id"}
        reason = args.get("reason", "Pelanggaran aturan group")
        count = await add_warning(chat_id, target_id, reason)
        result = {
            "success": True, "user_id": target_id,
            "warning_count": count, "reason": reason,
        }
        if count >= 3:
            duration = 10 if count < 5 else 60
            try:
                await mute_user(
                    bot=bot, chat_id=chat_id,
                    user_id=target_id, duration_minutes=duration,
                )
                result["auto_muted"] = True
                result["mute_duration_minutes"] = duration
            except Exception:
                result["auto_muted"] = False
        return result

    if tool_name == "get_warnings":
        target_id = args.get("user_id")
        if not target_id:
            return {"success": False, "error": "Missing user_id"}
        count = await get_count(chat_id, target_id)
        return {"success": True, "user_id": target_id, "warning_count": count}

    if tool_name == "reset_warnings":
        target_id = args.get("user_id")
        if not target_id:
            return {"success": False, "error": "Missing user_id"}
        await reset(chat_id, target_id)
        return {"success": True, "user_id": target_id, "warnings_reset": True}

    # \u2500\u2500 Voice chat tools \u2500\u2500
    if tool_name == "create_voice_chat":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="create_voice_chat",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED"}
        title = args.get("title")
        try:
            return await create_voice_chat(bot=bot, chat_id=chat_id, title=title)
        except Exception as e:
            return {"success": False, "error": str(e)}

    if tool_name == "end_voice_chat":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="end_voice_chat",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED"}
        try:
            return await end_voice_chat(bot=bot, chat_id=chat_id, voice_chat_id=0)
        except Exception as e:
            return {"success": False, "error": str(e)}

    # \u2500\u2500 Poll tool \u2500\u2500
    if tool_name == "create_poll":
        question = args.get("question", "")
        options = args.get("options", [])
        is_anonymous = args.get("is_anonymous", True)
        if len(options) < 2:
            return {"success": False, "error": "Minimal 2 pilihan."}
        try:
            return await create_poll(
                bot=bot, chat_id=chat_id, question=question,
                options=options, is_anonymous=is_anonymous,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    # \u2500\u2500 Slow mode tool \u2500\u2500
    if tool_name == "set_slow_mode":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="set_slow_mode",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED"}
        seconds = args.get("seconds", 0)
        try:
            return await set_slow_mode(bot=bot, chat_id=chat_id, seconds=seconds)
        except Exception as e:
            return {"success": False, "error": str(e)}

    # \u2500\u2500 Permission check for management tools \u2500\u2500
    allowed = await can_manage(
        bot=bot, chat_id=chat_id,
        user_id=user_id, action=tool_name,
    )
    if not allowed:
        return {
            "success": False, "error": "PERMISSION_DENIED",
            "message": "User tidak punya permission yang cukup.",
        }

    # \u2500\u2500 Auto-fill user_id from reply target \u2500\u2500
    target_tools = [
        "promote_user", "demote_user",
        "ban_user", "unban_user",
        "mute_user", "unmute_user",
    ]
    if tool_name in target_tools and "user_id" not in args:
        if message.reply_to_message and message.reply_to_message.from_user:
            args["user_id"] = message.reply_to_message.from_user.id
        else:
            return {"success": False, "error": "Missing user_id. Reply ke pesan user target."}

    # \u2500\u2500 Auto-fill message_id from reply target \u2500\u2500
    if tool_name in ["delete_message", "pin_message"] and "message_id" not in args:
        if message.reply_to_message:
            args["message_id"] = message.reply_to_message.message_id
        else:
            return {"success": False, "error": "Missing message_id. Reply ke pesan target."}

    # \u2500\u2500 Execute management tool \u2500\u2500
    try:
        dispatch = {
            "promote_user": lambda: promote_user(bot=bot, chat_id=chat_id, user_id=args["user_id"]),
            "demote_user": lambda: demote_user(bot=bot, chat_id=chat_id, user_id=args["user_id"]),
            "ban_user": lambda: ban_user(bot=bot, chat_id=chat_id, user_id=args["user_id"]),
            "unban_user": lambda: unban_user(bot=bot, chat_id=chat_id, user_id=args["user_id"]),
            "mute_user": lambda: mute_user(bot=bot, chat_id=chat_id, user_id=args["user_id"], duration_minutes=args.get("duration_minutes", 10)),
            "unmute_user": lambda: unmute_user(bot=bot, chat_id=chat_id, user_id=args["user_id"]),
            "delete_message": lambda: delete_message(bot=bot, chat_id=chat_id, message_id=args["message_id"]),
            "create_invite_link": lambda: create_invite_link(bot=bot, chat_id=chat_id),
            "pin_message": lambda: pin_message(bot=bot, chat_id=chat_id, message_id=args["message_id"]),
            "unpin_message": lambda: unpin_message(bot=bot, chat_id=chat_id, message_id=args.get("message_id")),
            "set_chat_title": lambda: set_chat_title(bot=bot, chat_id=chat_id, title=args["title"]),
            "set_chat_description": lambda: set_chat_description(bot=bot, chat_id=chat_id, description=args["description"]),
        }
        fn = dispatch.get(tool_name)
        if fn:
            return await fn()
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"success": False, "error": "UNKNOWN_TOOL"}


# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Handlers
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "\U0001f916 <b>Idol AI aktif.</b>\n\n"
        "Private chat \u2192 ngobrol santai.\n"
        "Group \u2192 assistant + moderator.\n\n"
        "Panggil aja \u201cidol\u201d di group!\n"
        "Developer: <a href=\"https://t.me/nathanidol\">Nathan Idol</a>",
        parse_mode="HTML",
    )


@dp.message(F.new_chat_members)
async def welcome_handler(message: Message):
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        name = user.full_name or "User"
        safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        await message.answer(
            f"\U0001f44b Selamat datang <b>{safe_name}</b>!\n"
            f"Salam kenal, ada yang bisa Idol bantu?",
            parse_mode="HTML",
        )


@dp.message()
async def message_handler(message: Message):
    if not message.text:
        return

    bot_info = await message.bot.get_me()
    chat_id = message.chat.id
    is_group = message.chat.type in ["group", "supergroup"]

    if is_group:
        mentioned = False
        if bot_info.username:
            mentioned = f"@{bot_info.username.lower()}" in message.text.lower()

        replied_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == bot_info.id
        )

        triggered = should_respond(message.text, bot_info.username)

        # \u2500\u2500 Check dismiss \u2500\u2500
        if is_dismiss(message.text):
            await end_conversation(chat_id)
            await add_message(
                chat_id=chat_id, role="user", content=message.text,
                user_id=message.from_user.id, user_name=message.from_user.full_name,
            )
            return

        # \u2500\u2500 Moderation (strict mode) \u2500\u2500
        strict = await get_strict_mode(chat_id)
        if strict and not mentioned and not replied_to_bot and not triggered:
            mod = await ai.check_moderation(message.text)
            if mod["category"] != "CLEAN" and mod["confidence"] > 0.7:
                user_name = message.from_user.full_name or "User"
                count = await add_warning(chat_id, message.from_user.id, mod["reason"])
                safe_name = user_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                warning = f"\u26a0\ufe0f <b>{safe_name}</b>, warning ke-{count}! ({mod['category']}: {mod['reason']})"
                if count >= 5:
                    try:
                        await mute_user(bot=message.bot, chat_id=chat_id, user_id=message.from_user.id, duration_minutes=60)
                        warning += "\n\U0001f507 Auto-mute 1 jam."
                    except Exception: pass
                    try:
                        await delete_message(bot=message.bot, chat_id=chat_id, message_id=message.message_id)
                    except Exception: pass
                elif count >= 3:
                    try:
                        await mute_user(bot=message.bot, chat_id=chat_id, user_id=message.from_user.id, duration_minutes=10)
                        warning += "\n\U0001f507 Auto-mute 10 menit."
                    except Exception: pass
                await message.answer(warning, parse_mode="HTML")
                await add_message(
                    chat_id=chat_id, role="user", content=message.text,
                    user_id=message.from_user.id, user_name=message.from_user.full_name,
                )
                return

        # \u2500\u2500 Check if bot should respond \u2500\u2500
        should_reply = mentioned or replied_to_bot or triggered

        # Check active conversation
        if not should_reply:
            conv_active = await is_conversation_active(chat_id)
            if conv_active:
                should_reply = True

        # Check nimbrung mode (proactive)
        if not should_reply:
            nimbrung_on = await get_nimbrung_mode(chat_id)
            if nimbrung_on:
                mod_result = await ai.check_should_join(message.text)
                if mod_result.get("should_join", False):
                    should_reply = True

        if not should_reply:
            await add_message(
                chat_id=chat_id, role="user", content=message.text,
                user_id=message.from_user.id, user_name=message.from_user.full_name,
            )
            return

        text = clean_trigger(message.text, bot_info.username)
        await mark_active(chat_id, topic_hint=text[:100])
    else:
        text = message.text

    # \u2500\u2500 Save & process \u2500\u2500
    await add_message(
        chat_id=chat_id, role="user", content=text,
        user_id=message.from_user.id, user_name=message.from_user.full_name,
    )

    context = await build_context(message)
    typing = TypingManager(message.bot, chat_id)
    await typing.start()

    try:
        async def tool_executor(name, args):
            return await execute_tool(
                bot=message.bot, message=message,
                tool_name=name, args=args,
            )

        response = await ai.chat(
            text=text, context=context,
            chat_id=chat_id, execute_tool_fn=tool_executor,
        )

        await add_message(chat_id=chat_id, role="assistant", content=response)

        if is_group:
            await mark_active(chat_id, topic_hint=text[:100])

        if response:
            clean = sanitize_html(response)
            if len(clean) > 4000:
                for i in range(0, len(clean), 4000):
                    chunk = clean[i:i+4000]
                    try:
                        await message.answer(chunk, parse_mode="HTML")
                    except Exception:
                        await message.answer(chunk)
            else:
                try:
                    await message.answer(clean, parse_mode="HTML")
                except Exception:
                    await message.answer(response)

    except Exception as e:
        print(f"\n{'='*40}", flush=True)
        print(f"AI ERROR: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        print(f"{'='*40}\n", flush=True)
        await message.answer("\u26a0\ufe0f Ada error waktu menjalankan perintah.")
    finally:
        await typing.stop()


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN belum ditemukan.")
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY belum ditemukan.")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    print("\U0001f916 Idol AI Group Assistant berjalan...", flush=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
