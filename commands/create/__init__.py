# type: ignore
from telegram import Update
from telegram.ext import (
	CallbackQueryHandler,
	CommandHandler,
	ContextTypes,
	ConversationHandler,
	MessageHandler,
	filters,
)

from commands.create.constants import CRYPTO, INDICATOR, COMPLETE
from commands.create.crypto import input_crypto, validate_crypto
from commands.create.indicator import next_button, previous_button


# from commands.create.indicators.price import price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	context.user_data.clear()
	context.user_data["pagination_offset"] = 0

	await update.message.reply_text("Let's get started! 🚀")
	return await input_crypto(update, context)


async def complete(update: Update, context=ContextTypes.DEFAULT_TYPE):
	if update.callback_query:
		await update.callback_query.edit_message_text(text="Done")
	else:
		await update.effective_message.reply_text(text="Done")

	print(context.user_data)

	return ConversationHandler.END


def command():
	indicator_selection = [
		# price(),
		CallbackQueryHandler(next_button, pattern="^next$"),
		CallbackQueryHandler(previous_button, pattern="^previous$"),
	]

	return ConversationHandler(
		entry_points=[CommandHandler("create", start)],
		states={
			CRYPTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_crypto)],
			INDICATOR: indicator_selection,
			COMPLETE: [CallbackQueryHandler(complete, pattern="^hihihihi$")],
		},
		fallbacks=[],
	)
