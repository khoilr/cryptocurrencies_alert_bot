import asyncio
import os
from warnings import filterwarnings

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, PicklePersistence
from telegram.warnings import PTBUserWarning

from bot.commands.create import command as create_command
from bot.commands.start import command as start_command
from bot.commands.pairs import command as pairs_command
from bot.logger import logger

# Remove CallbackQueryHandler per_* warning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# Load environment variables
load_dotenv()


def main():
    # Retrieve the telegram bot token from the environment
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", None)
    assert telegram_bot_token is not None

    # Persistent storage
    persistence = PicklePersistence(filepath="bot/persistence")

    # Create the application
    app = ApplicationBuilder().token(telegram_bot_token).persistence(persistence).build()

    # Add commands handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(pairs_command())
    app.add_handler(create_command())

    # Log bot info
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_info = loop.run_until_complete(app.bot.get_me())
    logger.info(f"Starting bot {bot_info.full_name}, id {bot_info.id}, token {telegram_bot_token}")

    # Long polling
    app.run_polling()


if __name__ == "__main__":
    main()
