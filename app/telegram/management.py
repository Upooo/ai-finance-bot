import time

from aiogram import Bot
from aiogram.types import ChatPermissions


async def get_group_info(bot: Bot, chat_id: int):
    chat = await bot.get_chat(chat_id)
    count = await bot.get_chat_member_count(chat_id)
    return {
        "success": True,
        "title": chat.title,
        "id": chat.id,
        "type": chat.type,
        "username": chat.username,
        "description": chat.description,
        "member_count": count,
    }


async def get_group_admins(bot: Bot, chat_id: int):
    admins = await bot.get_chat_administrators(chat_id=chat_id)
    result = []
    for admin in admins:
        result.append({
            "user_id": admin.user.id,
            "name": admin.user.full_name,
            "username": admin.user.username,
            "status": admin.status,
            "can_manage_chat": getattr(admin, "can_manage_chat", False),
            "can_delete_messages": getattr(admin, "can_delete_messages", False),
            "can_restrict_members": getattr(admin, "can_restrict_members", False),
            "can_promote_members": getattr(admin, "can_promote_members", False),
            "can_invite_users": getattr(admin, "can_invite_users", False),
            "can_pin_messages": getattr(admin, "can_pin_messages", False),
            "can_change_info": getattr(admin, "can_change_info", False),
            "can_manage_video_chats": getattr(admin, "can_manage_video_chats", False),
        })
    return {"success": True, "admins": result}


async def promote_user(bot: Bot, chat_id: int, user_id: int):
    await bot.promote_chat_member(
        chat_id=chat_id, user_id=user_id,
        can_manage_chat=True, can_delete_messages=True,
        can_manage_video_chats=True, can_restrict_members=True,
        can_invite_users=True, can_pin_messages=True,
        can_promote_members=True, can_change_info=True,
    )
    return {"success": True, "action": "promote", "user_id": user_id}


async def demote_user(bot: Bot, chat_id: int, user_id: int):
    await bot.promote_chat_member(
        chat_id=chat_id, user_id=user_id,
        can_manage_chat=False, can_delete_messages=False,
        can_manage_video_chats=False, can_restrict_members=False,
        can_invite_users=False, can_pin_messages=False,
        can_promote_members=False, can_change_info=False,
    )
    return {"success": True, "action": "demote", "user_id": user_id}


async def ban_user(bot: Bot, chat_id: int, user_id: int):
    await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    return {"success": True, "action": "ban", "user_id": user_id}


async def unban_user(bot: Bot, chat_id: int, user_id: int):
    await bot.unban_chat_member(
        chat_id=chat_id, user_id=user_id, only_if_banned=True,
    )
    return {"success": True, "action": "unban", "user_id": user_id}


async def mute_user(
    bot: Bot, chat_id: int, user_id: int,
    duration_minutes: int = 10,
):
    until_date = int(time.time()) + (duration_minutes * 60)
    permissions = ChatPermissions(
        can_send_messages=False, can_send_audios=False,
        can_send_documents=False, can_send_photos=False,
        can_send_videos=False, can_send_video_notes=False,
        can_send_voice_notes=False, can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
    )
    await bot.restrict_chat_member(
        chat_id=chat_id, user_id=user_id,
        permissions=permissions, until_date=until_date,
    )
    return {
        "success": True, "action": "mute",
        "user_id": user_id,
        "duration_minutes": duration_minutes,
    }


async def unmute_user(bot: Bot, chat_id: int, user_id: int):
    permissions = ChatPermissions(
        can_send_messages=True, can_send_audios=True,
        can_send_documents=True, can_send_photos=True,
        can_send_videos=True, can_send_video_notes=True,
        can_send_voice_notes=True, can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )
    await bot.restrict_chat_member(
        chat_id=chat_id, user_id=user_id,
        permissions=permissions,
    )
    return {"success": True, "action": "unmute", "user_id": user_id}


async def delete_message(bot: Bot, chat_id: int, message_id: int):
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    return {"success": True, "action": "delete_message", "message_id": message_id}


async def create_invite_link(bot: Bot, chat_id: int):
    invite = await bot.create_chat_invite_link(chat_id=chat_id)
    return {"success": True, "invite_link": invite.invite_link}


async def pin_message(bot: Bot, chat_id: int, message_id: int):
    await bot.pin_chat_message(chat_id=chat_id, message_id=message_id)
    return {"success": True, "action": "pin_message", "message_id": message_id}


async def unpin_message(bot: Bot, chat_id: int, message_id: int = None):
    if message_id:
        await bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)
    else:
        await bot.unpin_all_chat_messages(chat_id=chat_id)
    return {"success": True, "action": "unpin_message"}


async def set_chat_title(bot: Bot, chat_id: int, title: str):
    await bot.set_chat_title(chat_id=chat_id, title=title)
    return {"success": True, "action": "set_chat_title", "title": title}


async def set_chat_description(bot: Bot, chat_id: int, description: str):
    await bot.set_chat_description(chat_id=chat_id, description=description)
    return {"success": True, "action": "set_chat_description"}


async def get_member_count(bot: Bot, chat_id: int):
    count = await bot.get_chat_member_count(chat_id)
    return {"success": True, "member_count": count}


async def create_voice_chat(bot: Bot, chat_id: int, title: str = None):
    """Create/start a voice chat (video chat) in group."""
    try:
        await bot.create_forum_topic(
            chat_id=chat_id, name="Voice Chat",
        )
    except Exception:
        pass
    # Bot API: createVideoChatStarted
    result = await bot.create_video_chat(chat_id=chat_id, title=title)
    return {
        "success": True,
        "action": "create_voice_chat",
        "voice_chat_id": result.id if hasattr(result, 'id') else None,
    }


async def end_voice_chat(bot: Bot, chat_id: int, voice_chat_id: int):
    """End a voice chat (video chat) in group."""
    await bot.end_video_chat(chat_id=chat_id)
    return {"success": True, "action": "end_voice_chat"}


async def create_poll(
    bot: Bot, chat_id: int, question: str,
    options: list, is_anonymous: bool = True,
    poll_type: str = "regular",
):
    """Create a poll in group."""
    from aiogram.types import InputPollOption
    poll_options = [InputPollOption(text=opt) for opt in options]
    result = await bot.send_poll(
        chat_id=chat_id, question=question,
        options=poll_options, is_anonymous=is_anonymous,
        type=poll_type,
    )
    return {
        "success": True, "action": "create_poll",
        "message_id": result.message_id,
    }


async def set_slow_mode(bot: Bot, chat_id: int, seconds: int = 0):
    """Set slow mode delay (0 = off)."""
    await bot.set_chat_slow_mode_delay(
        chat_id=chat_id, slow_mode_delay=seconds,
    )
    return {
        "success": True, "action": "set_slow_mode",
        "slow_mode_seconds": seconds,
    }
