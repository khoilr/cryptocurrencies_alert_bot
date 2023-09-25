from email.headerregistry import ContentTypeHeader
import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from commands.create import command as create_command
from commands.start import command as start_command

load_dotenv()


async def callback_minute(context: ContentTypeHeader.DEFAULT_TYPE):
    print("Khoicute")


def main():
    # Init the application
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    job_queue = app.job_queue
    job_minute = job_queue.run_repeating(callback_minute, interval=60, first=10)

    # Add commands handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(create_command())

    # Long polling
    app.run_polling()


if __name__ == "__main__":
    main()
