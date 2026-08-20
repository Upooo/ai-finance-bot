from app.config import OWNER_ID, ADMIN_IDS
from aiogram import Bot


async def get_role(bot: Bot, chat_id: int, user_id: int):
    return await bot.get_chat_member(
        chat_id=chat_id, user_id=user_id,
    )


def is_bot_admin(user_id: int) -> bool:
    """Check if user is a bot-level admin (can toggle bot modes)."""
    return user_id in ADMIN_IDS


def is_owner(user_id: int) -> bool:
    """Check if user is the bot owner."""
    return user_id == OWNER_ID


async def can_manage(
    bot: Bot,
    chat_id: int,
    user_id: int,
    action: str,
) -> bool:
    # Bot-level actions: only owner + admin IDs
    bot_level_actions = [
        "toggle_strict_mode",
        "toggle_chat_mode",
        "toggle_nimbrung",
    ]
    if action in bot_level_actions:
        return is_bot_admin(user_id)

    member = await get_role(bot=bot, chat_id=chat_id, user_id=user_id)

    # Owner can do everything
    if member.status == "creator":
        return True

    # Bot admins can also manage (even if not Telegram admin)
    if is_bot_admin(user_id):
        return True

    # Regular users cannot manage
    if member.status != "administrator":
        return False

    if action in ["promote_user", "demote_user"]:
        return bool(getattr(member, "can_promote_members", False))

    if action in ["ban_user", "unban_user", "mute_user", "unmute_user"]:
        return bool(getattr(member, "can_restrict_members", False))

    if action == "delete_message":
        return bool(getattr(member, "can_delete_messages", False))

    if action == "create_invite_link":
        return bool(getattr(member, "can_invite_users", False))

    if action in ["pin_message", "unpin_message"]:
        return bool(getattr(member, "can_pin_messages", False))

    if action in ["set_chat_title", "set_chat_description"]:
        return bool(getattr(member, "can_change_info", False))

    if action in ["create_voice_chat", "end_voice_chat"]:
        return bool(getattr(member, "can_manage_video_chats", False))

    if action in [
        "get_group_info",
        "get_group_admins",
        "warn_user",
        "get_warnings",
        "reset_warnings",
        "get_member_count",
        "create_poll",
        "set_slow_mode",
    ]:
        return True

    return False
