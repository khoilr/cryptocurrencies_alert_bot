import asyncio
import os

import telegram
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    Updater,
)

from commands.create import command as create_command
from commands.start import command as start_command
from commands.examples.nested_conversation import command as nested_conversation_command

load_dotenv()


async def send_words(bot: Application.bot) -> None:
    print("Khoicute")


async def setup(context: CallbackContext) -> None:
    await send_words(context.bot)


def main():
    # Init the application
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    # Add commands handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(create_command())

    # Long polling
    app.run_polling()


if __name__ == "__main__":
    main()
