import os
import logging
from html import escape

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

SHOP_NAME = "IVR SHOP"
SHOP_DESCRIPTION = "Diamond • UC • Game Packages"

SHOP_URL = "https://t.me/inverisel"
SUPPORT_URL = "https://t.me/iveriselkun"
SHOP_WEB_URL = "https://ngwemoe9162-ui.github.io/ivr-telegram-backend/"

# Welcome message auto-delete time
DELETE_AFTER_SECONDS = 10


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("IVR_WELCOME_BOT")


# ============================================================
# KEYBOARD
# ============================================================

def main_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 SHOP NOW",
                url=SHOP_WEB_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "📢 CHANNEL",
                url=SHOP_URL,
            ),
            InlineKeyboardButton(
                "💬 SUPPORT",
                url=SUPPORT_URL,
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ============================================================
# START COMMAND
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    name = escape(user.first_name or "there")

    text = (
        f"👋 Welcome, <b>{name}</b>!\n\n"
        f"💎 <b>{SHOP_NAME}</b>\n"
        f"{SHOP_DESCRIPTION}\n\n"
        f"⚡ Fast • Secure • Easy\n"
        f"🛍️ Thank you for visiting us!\n\n"
        f"✨ <i>Choose an option below.</i>"
    )

    await message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard(),
    )


# ============================================================
# HELP COMMAND
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.effective_message

    if not message:
        return

    text = (
        "🤖 <b>IVR SMART WELCOME BOT</b>\n\n"
        "Available commands:\n\n"
        "▶️ /start — Open shop menu\n"
        "▶️ /help — Show this help\n"
        "▶️ /id — Show chat/user ID\n"
        "▶️ /rules — Show group rules\n\n"
        "👋 New members automatically receive "
        "a welcome message."
    )

    await message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard(),
    )


# ============================================================
# ID COMMAND
# ============================================================

async def id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message:
        return

    user_id = user.id if user else "Unknown"
    chat_id = chat.id if chat else "Unknown"

    text = (
        "🆔 <b>ID INFORMATION</b>\n\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"💬 Chat ID: <code>{chat_id}</code>"
    )

    await message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# RULES COMMAND
# ============================================================

async def rules_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.effective_message

    if not message:
        return

    text = (
        "📜 <b>IVR SHOP GROUP RULES</b>\n\n"
        "1️⃣ Respect all members.\n"
        "2️⃣ No spam or flooding.\n"
        "3️⃣ No unwanted links or advertisements.\n"
        "4️⃣ No scams or fake promotions.\n"
        "5️⃣ Keep conversations appropriate.\n"
        "6️⃣ For orders, use the official shop.\n\n"
        "💎 Thank you for keeping our community clean!"
    )

    await message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard(),
    )


# ============================================================
# DELETE MESSAGE JOB
# ============================================================

async def delete_message_job(
    context: ContextTypes.DEFAULT_TYPE,
):

    job = context.job

    if not job:
        return

    data = job.data

    if not data:
        return

    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    if not chat_id or not message_id:
        return

    try:

        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        logger.info(
            "Temporary message deleted: %s",
            message_id,
        )

    except Exception as error:

        logger.warning(
            "Could not delete message %s: %s",
            message_id,
            error,
        )


# ============================================================
# SCHEDULE DELETE
# ============================================================

def schedule_delete(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    seconds: int,
):

    if not context.job_queue:

        logger.warning(
            "JobQueue is unavailable. "
            "Auto-delete cannot be scheduled."
        )

        return

    context.job_queue.run_once(
        delete_message_job,
        seconds,
        data={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )


# ============================================================
# WELCOME NEW MEMBERS
# ============================================================

async def welcome_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.effective_message

    if not message:
        return

    new_members = message.new_chat_members

    if not new_members:
        return

    # --------------------------------------------------------
    # Delete Telegram's default "joined the group" message
    # --------------------------------------------------------

    try:

        await message.delete()

        logger.info(
            "Telegram join service message deleted."
        )

    except Exception as error:

        logger.warning(
            "Could not delete join service message: %s",
            error,
        )

    # --------------------------------------------------------
    # Welcome each new member
    # --------------------------------------------------------

    for user in new_members:

        # Ignore bot accounts
        if user.is_bot:
            logger.info(
                "Ignoring bot account: %s",
                user.id,
            )
            continue

        name = escape(
            user.first_name or "there"
        )

        welcome_text = (
            f"👋 <b>WELCOME, {name.upper()}!</b>\n\n"
            f"💎 <b>{SHOP_NAME}</b>\n\n"
            f"🎮 Diamond • UC • Game Packages\n"
            f"⚡ Fast Delivery\n"
            f"🔐 Safe & Secure\n"
            f"💯 Trusted Service\n\n"
            f"✨ <i>We're happy to have you here!</i>\n\n"
            f"👇 <b>Choose an option below</b>"
        )

        try:

            sent_message = await context.bot.send_message(
                chat_id=message.chat_id,
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=main_keyboard(),
            )

            schedule_delete(
                context=context,
                chat_id=sent_message.chat_id,
                message_id=sent_message.message_id,
                seconds=DELETE_AFTER_SECONDS,
            )

            logger.info(
                "Welcome message sent to %s "
                "(%s). Auto-delete: %s seconds.",
                user.full_name,
                user.id,
                DELETE_AFTER_SECONDS,
            )

        except Exception as error:

            logger.error(
                "Could not send welcome message: %s",
                error,
            )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

    error = context.error

    logger.error(
        "Unhandled exception:",
        exc_info=error,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Check token
    # --------------------------------------------------------

    if not BOT_TOKEN:

        print()
        print("================================")
        print("   IVR SMART WELCOME BOT")
        print("================================")
        print("❌ ERROR")
        print("BOT_TOKEN is not configured.")
        print()
        print("Add BOT_TOKEN in Render Environment Variables.")
        print("================================")

        return

    # --------------------------------------------------------
    # Create application
    # --------------------------------------------------------

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # --------------------------------------------------------
    # Commands
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "id",
            id_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "rules",
            rules_command,
        )
    )

    # --------------------------------------------------------
    # New members
    # --------------------------------------------------------

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_new_member,
        )
    )

    # --------------------------------------------------------
    # Error handler
    # --------------------------------------------------------

    app.add_error_handler(
        error_handler,
    )

    # --------------------------------------------------------
    # Startup information
    # --------------------------------------------------------

    print()
    print("================================")
    print("     IVR SMART WELCOME BOT")
    print("================================")
    print("👋 Welcome system: ON")
    print("🗑️ Auto-delete: 10 seconds")
    print("🧹 Join message cleanup: ON")
    print("🔘 Shop buttons: ON")
    print("📢 Channel button: ON")
    print("💬 Support button: ON")
    print("📜 Rules command: ON")
    print("🆔 ID command: ON")
    print("🤖 Bot is running...")
    print("================================")
    print()

    # --------------------------------------------------------
    # Start polling
    # --------------------------------------------------------

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
