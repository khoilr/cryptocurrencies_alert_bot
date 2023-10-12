import os
from warnings import filterwarnings

from dotenv import load_dotenv
from loguru import logger
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.warnings import PTBUserWarning

from commands.create import command as create_command
from commands.start import command as start_command

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
load_dotenv()


def main():
	# Retrieve the telegram bot token from the environment
	telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", None)
	assert telegram_bot_token is not None

	# Create the application
	app = ApplicationBuilder().token(telegram_bot_token).build()

	# Add commands handlers
	app.add_handler(CommandHandler("start", start_command))
	app.add_handler(create_command())

	# Log bot info
	logger.info(f"Starting bot {app.bot}")

	# Long polling
	app.run_polling()


if __name__ == "__main__":
	main()
