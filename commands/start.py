# type: ignore
from telegram import Update
from telegram.ext import CallbackContext

from stream.database.models.dao.user import User as User_DAO


async def command(update: Update, context: CallbackContext) -> None:  # pylint: disable=unused-argument
	# Send a welcome message and introduce the bot's features to the user.
	effective_user = update.effective_user
	user = User_DAO.upsert(**effective_user.to_dict())
	print(user)
	await update.message.reply_text("Welcome")
