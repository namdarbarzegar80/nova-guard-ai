from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatPermissions


async def is_admin(
    bot: Bot,
    chat_id: int,
    user_id: int
) -> bool:

    member = await bot.get_chat_member(
        chat_id,
        user_id
    )

    return member.status in {
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    }


async def mute_user(
    bot: Bot,
    chat_id: int,
    user_id: int,
    seconds: int = 0
):

    permissions = ChatPermissions(
        can_send_messages=False
    )

    until_date = None

    if seconds > 0:
        import time

        until_date = int(time.time()) + seconds

    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=permissions,
        until_date=until_date
    )


async def unmute_user(
    bot: Bot,
    chat_id: int,
    user_id: int
):

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=permissions
    )


async def ban_user(
    bot: Bot,
    chat_id: int,
    user_id: int
):

    await bot.ban_chat_member(
        chat_id=chat_id,
        user_id=user_id
    )


async def unban_user(
    bot: Bot,
    chat_id: int,
    user_id: int
):

    await bot.unban_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        only_if_banned=True
    )
