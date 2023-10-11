import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from commands.create import command as create_command
from commands.start import command as start_command

load_dotenv()


def main():
    # Init the application
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", None)

    assert telegram_bot_token is not None

    app = ApplicationBuilder().token(telegram_bot_token).build()

    # job_queue = app.job_queue
    # job_minute = job_queue.run_repeating(callback_minute, interval=60, first=10)

    # Add commands handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(create_command())

    # Long polling
    app.run_polling()


if __name__ == "__main__":
    main()
