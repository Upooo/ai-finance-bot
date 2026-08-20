from aiogram import Bot


async def get_role(
    bot: Bot,
    chat_id: int,
    user_id: int,
):
    return await bot.get_chat_member(
        chat_id=chat_id,
        user_id=user_id,
    )


async def can_manage(
    bot: Bot,
    chat_id: int,
    user_id: int,
    action: str,
):
    member = await get_role(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
    )

    # Owner selalu boleh.
    if member.status == "creator":
        return True

    # User biasa tidak boleh melakukan management.
    if member.status != "administrator":
        return False

    if action in [
        "promote_user",
        "demote_user",
    ]:
        return bool(
            getattr(
                member,
                "can_promote_members",
                False,
            )
        )

    if action in [
        "ban_user",
        "unban_user",
        "mute_user",
        "unmute_user",
    ]:
        return bool(
            getattr(
                member,
                "can_restrict_members",
                False,
            )
        )

    if action == "delete_message":
        return bool(
            getattr(
                member,
                "can_delete_messages",
                False,
            )
        )

    if action == "create_invite_link":
        return bool(
            getattr(
                member,
                "can_invite_users",
                False,
            )
        )

    if action in [
        "get_group_info",
        "get_group_admins",
    ]:
        return True

    return False
