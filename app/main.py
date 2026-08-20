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
)
from app.storage.settings import (
    get_strict_mode, set_strict_mode,
    get_chat_mode, set_chat_mode,
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
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

dp = Dispatcher()
ai = AIAgent(GROQ_API_KEY)


# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Helpers
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def escape_html(text: str) -> str:
    if not text:
        return ""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


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

    # \u2500\u2500 Settings tools (admin-only) \u2500\u2500
    if tool_name == "toggle_strict_mode":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="toggle_strict_mode",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED"}
        enabled = args.get("enabled", False)
        await set_strict_mode(chat_id, enabled)
        return {"success": True, "strict_mode": enabled}

    if tool_name == "toggle_chat_mode":
        allowed = await can_manage(
            bot=bot, chat_id=chat_id,
            user_id=user_id, action="toggle_chat_mode",
        )
        if not allowed:
            return {"success": False, "error": "PERMISSION_DENIED"}
        enabled = args.get("enabled", False)
        await set_chat_mode(chat_id, enabled)
        if not enabled:
            await end_conversation(chat_id)
        return {"success": True, "chat_mode": enabled}

    # \u2500\u2500 Warning tools \u2500\u2500
    if tool_name == "warn_user":
        target_id = args.get("user_id")
        if not target_id:
            return {"success": False, "error": "Missing user_id"}
        reason = args.get("reason", "Pelanggaran aturan group")
        count = await add_warning(chat_id, target_id, reason)
        result = {
            "success": True,
            "user_id": target_id,
            "warning_count": count,
            "reason": reason,
        }
        if count >= 3:
            duration = 10 if count < 5 else 60
            try:
                await mute_user(
                    bot=bot, chat_id=chat_id,
                    user_id=target_id,
                    duration_minutes=duration,
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
        return {
            "success": True,
            "user_id": target_id,
            "warning_count": count,
        }

    # \u2500\u2500 Permission check for management tools \u2500\u2500
    allowed = await can_manage(
        bot=bot, chat_id=chat_id,
        user_id=user_id, action=tool_name,
    )
    if not allowed:
        return {
            "success": False,
            "error": "PERMISSION_DENIED",
            "message": "User tidak punya permission yang cukup.",
        }

    # \u2500\u2500 Auto-fill user_id from reply target \u2500\u2500
    target_tools = [
        "promote_user", "demote_user",
        "ban_user", "unban_user",
        "mute_user", "unmute_user",
    ]
    if tool_name in target_tools and "user_id" not in args:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user
        ):
            args["user_id"] = message.reply_to_message.from_user.id
        else:
            return {
                "success": False,
                "error": "Missing user_id. Reply ke pesan user target.",
            }

    # \u2500\u2500 Auto-fill message_id from reply target \u2500\u2500
    if tool_name == "delete_message" and "message_id" not in args:
        if message.reply_to_message:
            args["message_id"] = message.reply_to_message.message_id
        else:
            return {
                "success": False,
                "error": "Missing message_id. Reply ke pesan yang mau dihapus.",
            }
    if tool_name == "pin_message" and "message_id" not in args:
        if message.reply_to_message:
            args["message_id"] = message.reply_to_message.message_id
        else:
            return {
                "success": False,
                "error": "Missing message_id. Reply ke pesan yang mau di-pin.",
            }

    # \u2500\u2500 Execute management tool \u2500\u2500
    try:
        dispatch = {
            "promote_user": lambda: promote_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
            ),
            "demote_user": lambda: demote_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
            ),
            "ban_user": lambda: ban_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
            ),
            "unban_user": lambda: unban_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
            ),
            "mute_user": lambda: mute_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
                duration_minutes=args.get("duration_minutes", 10),
            ),
            "unmute_user": lambda: unmute_user(
                bot=bot, chat_id=chat_id, user_id=args["user_id"],
            ),
            "delete_message": lambda: delete_message(
                bot=bot, chat_id=chat_id, message_id=args["message_id"],
            ),
            "create_invite_link": lambda: create_invite_link(
                bot=bot, chat_id=chat_id,
            ),
            "pin_message": lambda: pin_message(
                bot=bot, chat_id=chat_id, message_id=args["message_id"],
            ),
            "unpin_message": lambda: unpin_message(
                bot=bot, chat_id=chat_id,
                message_id=args.get("message_id"),
            ),
            "set_chat_title": lambda: set_chat_title(
                bot=bot, chat_id=chat_id, title=args["title"],
            ),
            "set_chat_description": lambda: set_chat_description(
                bot=bot, chat_id=chat_id,
                description=args["description"],
            ),
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
        "Panggil aja \u201cidol\u201d di group!",
        parse_mode="HTML",
    )


@dp.message(F.new_chat_members)
async def welcome_handler(message: Message):
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        name = user.full_name or "User"
        await message.answer(
            f"\U0001f44b Selamat datang <b>{escape_html(name)}</b>!\n"
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

    # \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
    # GROUP FILTER
    # \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
    if is_group:
        mentioned = False
        if bot_info.username:
            mentioned = (
                f"@{bot_info.username.lower()}"
                in message.text.lower()
            )

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
                chat_id=chat_id, role="user",
                content=message.text,
                user_id=message.from_user.id,
                user_name=message.from_user.full_name,
            )
            return  # Bot stays silent

        # \u2500\u2500 Moderation (strict mode) \u2500\u2500
        strict = await get_strict_mode(chat_id)
        if strict and not mentioned and not replied_to_bot and not triggered:
            mod = await ai.check_moderation(message.text)
            if (
                mod["category"] != "CLEAN"
                and mod["confidence"] > 0.7
            ):
                user_name = message.from_user.full_name or "User"
                count = await add_warning(
                    chat_id, message.from_user.id, mod["reason"],
                )
                warning = (
                    f"\u26a0\ufe0f {user_name}, warning ke-{count}! "
                    f"({mod['category']}: {mod['reason']})"
                )
                if count >= 5:
                    try:
                        await mute_user(
                            bot=message.bot, chat_id=chat_id,
                            user_id=message.from_user.id,
                            duration_minutes=60,
                        )
                        warning += "\n\U0001f507 Auto-mute 1 jam."
                    except Exception:
                        pass
                    try:
                        await delete_message(
                            bot=message.bot, chat_id=chat_id,
                            message_id=message.message_id,
                        )
                    except Exception:
                        pass
                elif count >= 3:
                    try:
                        await mute_user(
                            bot=message.bot, chat_id=chat_id,
                            user_id=message.from_user.id,
                            duration_minutes=10,
                        )
                        warning += "\n\U0001f507 Auto-mute 10 menit."
                    except Exception:
                        pass
                await message.answer(warning)

                await add_message(
                    chat_id=chat_id, role="user",
                    content=message.text,
                    user_id=message.from_user.id,
                    user_name=message.from_user.full_name,
                )
                return

        # \u2500\u2500 Check if bot should respond \u2500\u2500
        should_reply = mentioned or replied_to_bot or triggered

        # Check active conversation (bot already engaged)
        if not should_reply:
            conv_active = await is_conversation_active(chat_id)
            if conv_active:
                should_reply = True  # Bot stays in conversation

        # Check chat mode (proactive nimbrung)
        if not should_reply:
            chat_mode_on = await get_chat_mode(chat_id)
            if chat_mode_on:
                # Ask AI if it should join this conversation
                mod_result = await ai.check_should_join(message.text)
                if mod_result.get("should_join", False):
                    should_reply = True

        if not should_reply:
            # Save to history but don't respond
            await add_message(
                chat_id=chat_id, role="user",
                content=message.text,
                user_id=message.from_user.id,
                user_name=message.from_user.full_name,
            )
            return

        text = clean_trigger(message.text, bot_info.username)

        # Mark conversation as active
        await mark_active(chat_id, topic_hint=text[:100])
    else:
        text = message.text

    # \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
    # SAVE & PROCESS
    # \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
    await add_message(
        chat_id=chat_id, role="user", content=text,
        user_id=message.from_user.id,
        user_name=message.from_user.full_name,
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
            text=text,
            context=context,
            chat_id=chat_id,
            execute_tool_fn=tool_executor,
        )

        # Save AI response to history
        await add_message(
            chat_id=chat_id, role="assistant", content=response,
        )

        # Refresh active conversation timer
        if is_group:
            await mark_active(chat_id, topic_hint=text[:100])

        # Send response (split if too long)
        if response:
            if len(response) > 4000:
                for i in range(0, len(response), 4000):
                    chunk = response[i : i + 4000]
                    await message.answer(
                        escape_html(chunk), parse_mode="HTML",
                    )
            else:
                await message.answer(
                    escape_html(response), parse_mode="HTML",
                )

    except Exception as e:
        print(f"\n{'=' * 40}", flush=True)
        print("AI ERROR", flush=True)
        print(f"TYPE: {type(e).__name__}", flush=True)
        print(f"MESSAGE: {e}", flush=True)
        traceback.print_exc()
        print(f"{'=' * 40}\n", flush=True)
        await message.answer(
            "\u26a0\ufe0f Ada error waktu menjalankan perintah.",
        )
    finally:
        await typing.stop()


# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Main
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

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
