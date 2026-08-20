import asyncio
import os
import traceback

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from app.telegram.context import build_context
from app.ai.agent import AIAgent
from app.telegram.permissions import can_manage

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
)


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


dp = Dispatcher()

ai = AIAgent(
    GROQ_API_KEY
)


def escape_html(text: str) -> str:
    """
    Escape karakter HTML agar response AI
    tidak membuat Telegram gagal parse.
    """

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

    # =====================================
    # READ-ONLY TOOLS
    # =====================================

    if tool_name == "get_group_info":

        return await get_group_info(
            bot=bot,
            chat_id=chat_id,
        )

    if tool_name == "get_group_admins":

        return await get_group_admins(
            bot=bot,
            chat_id=chat_id,
        )

    # =====================================
    # PERMISSION CHECK
    # =====================================

    allowed = await can_manage(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        action=tool_name,
    )

    if not allowed:

        return {
            "success": False,
            "error": "PERMISSION_DENIED",
            "message": (
                "User yang meminta tindakan "
                "tidak mempunyai permission "
                "yang cukup."
            ),
        }

    # =====================================
    # PROMOTE
    # =====================================

    if tool_name == "promote_user":

        return await promote_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # DEMOTE
    # =====================================

    if tool_name == "demote_user":

        return await demote_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # BAN
    # =====================================

    if tool_name == "ban_user":

        return await ban_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # UNBAN
    # =====================================

    if tool_name == "unban_user":

        return await unban_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # MUTE
    # =====================================

    if tool_name == "mute_user":

        return await mute_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # UNMUTE
    # =====================================

    if tool_name == "unmute_user":

        return await unmute_user(
            bot=bot,
            chat_id=chat_id,
            user_id=args["user_id"],
        )

    # =====================================
    # DELETE MESSAGE
    # =====================================

    if tool_name == "delete_message":

        return await delete_message(
            bot=bot,
            chat_id=chat_id,
            message_id=args["message_id"],
        )

    # =====================================
    # INVITE LINK
    # =====================================

    if tool_name == "create_invite_link":

        return await create_invite_link(
            bot=bot,
            chat_id=chat_id,
        )

    return {
        "success": False,
        "error": "UNKNOWN_TOOL",
    }


@dp.message(
    CommandStart()
)
async def start_handler(
    message: Message,
):

    await message.answer(
        "🤖 <b>Idol AI aktif.</b>\n\n"
        "Private chat + Group Assistant.",
        parse_mode="HTML",
    )


@dp.message()
async def message_handler(
    message: Message,
):

    if not message.text:
        return

    context = await build_context(
        message
    )

    # =====================================
    # GROUP FILTER
    # =====================================

    if message.chat.type in [
        "group",
        "supergroup",
    ]:

        bot_info = await message.bot.get_me()

        mentioned = False

        if bot_info.username:

            mentioned = (
                f"@{bot_info.username.lower()}"
                in message.text.lower()
            )

        replied_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and (
                message.reply_to_message
                .from_user.id
                == bot_info.id
            )
        )

        if not mentioned and not replied_to_bot:
            return

        text = message.text

        if bot_info.username:

            text = text.replace(
                f"@{bot_info.username}",
                "",
            ).strip()

    else:

        text = message.text

    # =====================================
    # AI PROCESSING
    # =====================================

    try:

        decision = await ai.decide(
            text=text,
            context=context,
        )

        # =================================
        # NORMAL CHAT
        # =================================

        if decision["type"] == "text":

            response = escape_html(
                decision["text"]
            )

            await message.answer(
                response,
                parse_mode="HTML",
            )

            return

        # =================================
        # TOOL CALL
        # =================================

        results = []

        for call in decision["calls"]:

            tool_name = call["name"]

            args = call.get(
                "args",
                {},
            )

            # -----------------------------
            # REPLY TARGET
            # -----------------------------

            target_tools = [
                "promote_user",
                "demote_user",
                "ban_user",
                "unban_user",
                "mute_user",
                "unmute_user",
            ]

            if (
                "user_id" not in args
                and context.get("reply")
                and context["reply"].get("user")
                and tool_name in target_tools
            ):

                args["user_id"] = (
                    context["reply"]
                    ["user"]
                    ["id"]
                )

            # -----------------------------
            # DELETE REPLY TARGET
            # -----------------------------

            if (
                tool_name == "delete_message"
                and "message_id" not in args
                and context.get("reply")
            ):

                args["message_id"] = (
                    context["reply"]
                    ["message_id"]
                )

            # -----------------------------
            # EXECUTE
            # -----------------------------

            print(
                f"[TOOL] {tool_name} "
                f"ARGS={args}",
                flush=True,
            )

            result = await execute_tool(
                bot=message.bot,
                message=message,
                tool_name=tool_name,
                args=args,
            )

            print(
                f"[TOOL RESULT] {result}",
                flush=True,
            )

            results.append({
                "tool": tool_name,
                "args": args,
                "result": result,
            })

        # =================================
        # FINAL RESPONSE
        # =================================

        final = await ai.final_response(
            text=text,
            context=context,
            results=results,
        )

        await message.answer(
            escape_html(final),
            parse_mode="HTML",
        )

    except Exception as e:

        print(
            "\n==============================",
            flush=True,
        )

        print(
            "AI ERROR",
            flush=True,
        )

        print(
            f"TYPE: {type(e).__name__}",
            flush=True,
        )

        print(
            f"MESSAGE: {e}",
            flush=True,
        )

        traceback.print_exc()

        print(
            "==============================\n",
            flush=True,
        )

        await message.answer(
            "⚠️ Ada error waktu menjalankan "
            "perintah.",
        )


async def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN belum ditemukan."
        )

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY belum ditemukan."
        )

    bot = Bot(
        token=BOT_TOKEN,
    )

    print(
        "🤖 Idol AI Group Assistant berjalan...",
        flush=True,
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
