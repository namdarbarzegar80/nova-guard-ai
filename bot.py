import asyncio
from collections import defaultdict, deque
from time import monotonic

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, BOT_NAME, OWNER_ID

from database import (
    init_db,
    ensure_group,
    get_settings,
    set_setting,
    add_warning,
    add_word,
    remove_word,
    get_words
)

from filters import has_link, contains_bad_word

from moderation import (
    is_admin,
    mute_user,
    unmute_user,
    ban_user,
    unban_user
)


bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

flood = defaultdict(deque)


async def admin_only(message: Message):

    if message.from_user.id == OWNER_ID:
        return True

    if message.chat.type not in {
        ChatType.GROUP,
        ChatType.SUPERGROUP
    }:
        return False

    return await is_admin(
        bot,
        message.chat.id,
        message.from_user.id
    )


@dp.message(Command("start"))
async def start(message: Message):

    await message.answer(
        f"🛡️ <b>{BOT_NAME}</b> فعال است.\n\n"
        "برای راهنما /help را بفرست."
    )


@dp.message(Command("help"))
async def help_command(message: Message):

    await message.answer(
        "📚 <b>راهنمای Nova Guard AI</b>\n\n"
        "🔨 مدیریت:\n"
        "/ban\n"
        "/unban\n"
        "/mute\n"
        "/unmute\n\n"
        "⚙️ تنظیمات:\n"
        "/settings\n\n"
        "🇮🇷 دستورات فارسی:\n"
        "ربات\n"
        "راهنما\n"
        "وضعیت\n"
        "ضدلینک روشن\n"
        "ضدلینک خاموش\n"
        "ضدفlood روشن\n"
        "ضدفlood خاموش\n"
        "فیلتر کلمه\n"
        "حذف فیلتر کلمه\n"
        "لیست فیلتر"
    )


@dp.message(Command("settings"))
async def settings_command(message: Message):

    if not await admin_only(message):
        await message.answer(
            "⛔ این دستور فقط برای مدیران است."
        )
        return

    await ensure_group(message.chat.id)

    settings = await get_settings(
        message.chat.id
    )

    await message.answer(
        "⚙️ <b>تنظیمات گروه</b>\n\n"
        f"🔗 ضدلینک: {'روشن' if settings[1] else 'خاموش'}\n"
        f"🌊 ضدفلود: {'روشن' if settings[2] else 'خاموش'}\n"
        f"👋 خوش‌آمد: {'روشن' if settings[3] else 'خاموش'}\n"
        f"⚠️ حد اخطار: {settings[4]}"
    )


async def action_on_reply(
    message: Message,
    action: str
):

    if not await admin_only(message):
        await message.answer(
            "⛔ این دستور فقط برای مدیران است."
        )
        return

    if not message.reply_to_message:
        await message.answer(
            "↩️ روی پیام کاربر ریپلای کن."
        )
        return

    target = message.reply_to_message.from_user

    try:

        if action == "ban":
            await ban_user(
                bot,
                message.chat.id,
                target.id
            )
            text = "🚷 کاربر بن شد."

        elif action == "unban":
            await unban_user(
                bot,
                message.chat.id,
                target.id
            )
            text = "✅ کاربر آن‌بن شد."

        elif action == "mute":
            await mute_user(
                bot,
                message.chat.id,
                target.id,
                3600
            )
            text = "🔇 کاربر یک ساعت میوت شد."

        elif action == "unmute":
            await unmute_user(
                bot,
                message.chat.id,
                target.id
            )
            text = "🔊 کاربر آزاد شد."

        else:
            return

        await message.answer(text)

    except Exception as error:

        print(error)

        await message.answer(
            "❌ عملیات انجام نشد. دسترسی‌های ربات را بررسی کن."
        )


@dp.message(Command("ban"))
async def ban_command(message: Message):
    await action_on_reply(message, "ban")


@dp.message(Command("unban"))
async def unban_command(message: Message):
    await action_on_reply(message, "unban")


@dp.message(Command("mute"))
async def mute_command(message: Message):
    await action_on_reply(message, "mute")


@dp.message(Command("unmute"))
async def unmute_command(message: Message):
    await action_on_reply(message, "unmute")


@dp.message(F.text)
async def text_handler(message: Message):

    text = message.text.strip()
    low = text.lower()

    # صدا زدن ربات
    if low in {
        "ربات",
        "ربات؟",
        "هی ربات"
    }:

        await message.answer(
            "🤖 جانم؟\n"
            "بگو چه کاری انجام بدم."
        )

        return

    if message.chat.type not in {
        ChatType.GROUP,
        ChatType.SUPERGROUP
    }:
        return

    await ensure_group(
        message.chat.id
    )

    settings = await get_settings(
        message.chat.id
    )

    # راهنما
    if low in {"راهنما", "کمک"}:
        await help_command(message)
        return

    # وضعیت
    if low == "وضعیت":
        await settings_command(message)
        return

    # ضدلینک
    if low == "ضدلینک روشن":

        if await admin_only(message):

            await set_setting(
                message.chat.id,
                "anti_link",
                1
            )

            await message.answer(
                "🔗 ضدلینک روشن شد."
            )

        return

    if low == "ضدلینک خاموش":

        if await admin_only(message):

            await set_setting(
                message.chat.id,
                "anti_link",
                0
            )

            await message.answer(
                "🔗 ضدلینک خاموش شد."
            )

        return

    # ضدفلود
    if low == "ضدفlood روشن":

        if await admin_only(message):

            await set_setting(
                message.chat.id,
                "anti_flood",
                1
            )

            await message.answer(
                "🌊 ضدفلود روشن شد."
            )

        return

    if low == "ضدفlood خاموش":

        if await admin_only(message):

            await set_setting(
                message.chat.id,
                "anti_flood",
                0
            )

            await message.answer(
                "🌊 ضدفلود خاموش شد."
            )

        return

    # افزودن کلمه
    if low.startswith("فیلتر "):

        if await admin_only(message):

            word = text[7:].strip()

            if word:

                await add_word(
                    message.chat.id,
                    word
                )

                await message.answer(
                    f"🚫 «{word}» به فیلتر اضافه شد."
                )

        return

    # حذف کلمه
    if low.startswith("حذف فیلتر "):

        if await admin_only(message):

            word = text[10:].strip()

            if word:

                await remove_word(
                    message.chat.id,
                    word
                )

                await message.answer(
                    f"✅ «{word}» از فیلتر حذف شد."
                )

        return

    # لیست فیلتر
    if low == "لیست فیلتر":

        if not await admin_only(message):
            return

        words = await get_words(
            message.chat.id
        )

        if words:
            result = "\n".join(
                f"• {word}"
                for word in words
            )
        else:
            result = "خالی است."

        await message.answer(
            "🚫 <b>لیست فیلتر</b>\n\n"
            + result
        )

        return

    # مدیران از فیلتر عبور کنند
    if await admin_only(message):
        return

    # ضدلینک
    if settings[1] and has_link(text):

        try:
            await message.delete()
        except Exception:
            pass

        await message.answer(
            "🚫 ارسال لینک در این گروه مجاز نیست."
        )

        return

    # فیلتر کلمات
    words = await get_words(
        message.chat.id
    )

    if contains_bad_word(text, words):

        try:
            await message.delete()
        except Exception:
            pass

        count = await add_warning(
            message.chat.id,
            message.from_user.id
        )

        limit = settings[4]

        await message.answer(
            f"⚠️ {message.from_user.mention_html()} "
            f"اخطار {count}/{limit}"
        )

        if count >= limit:

            try:
                await mute_user(
                    bot,
                    message.chat.id,
                    message.from_user.id,
                    3600
                )

                await message.answer(
                    "🔇 به دلیل رسیدن به حد اخطار، "
                    "کاربر یک ساعت میوت شد."
                )

            except Exception as error:
                print(error)

        return

    # ضدفلود
    if settings[2]:

        now = monotonic()

        key = (
            message.chat.id,
            message.from_user.id
        )

        queue = flood[key]

        queue.append(now)

        while queue and now - queue[0] > 5:
            queue.popleft()

        if len(queue) >= 8:

            try:

                await mute_user(
                    bot,
                    message.chat.id,
                    message.from_user.id,
                    60
                )

                queue.clear()

                await message.answer(
                    "🌊 به دلیل فلود، "
                    "کاربر ۱ دقیقه میوت شد."
                )

            except Exception as error:
                print(error)


async def main():

    await init_db()

    print(
        f"{BOT_NAME} is running..."
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
