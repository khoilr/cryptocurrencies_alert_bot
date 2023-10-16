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

from bot.commands.create.constants import CRYPTO, INDICATOR, COMPLETE, create_welcome_message
from bot.commands.create.crypto import input_crypto, validate_crypto
from bot.commands.create.indicator import next_button, previous_button
from bot.commands.create.indicators.price import price
from database.models.dao.alert import Alert as AlertDAO
from database.models.dao.crypto import Crypto as CryptoDAO
from database.models.dao.indicator import Indicator as IndicatorDAO
from database.models.dao.user import User as UserDAO


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pagination_offset"] = 0

    await update.message.reply_text(create_welcome_message)
    return await input_crypto(update, context)


async def complete(update: Update, context=ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text(text="Done")
    else:
        await update.effective_message.reply_text(text="Done")

    user_data = context.user_data
    print(user_data)

    # finder user
    user = UserDAO.select_one(id=update.effective_user.id)

    # cryptos
    cryptos = CryptoDAO.get_multiple_by_symbols(user_data["cryptos"])

    # indicator
    indicator_objs = [IndicatorDAO.insert(**indicator_user_data) for indicator_user_data in user_data["indicators"]]

    # alert
    alert = AlertDAO.insert(user=user, cryptos=cryptos, indicators=indicator_objs)

    print(user)
    print(cryptos)
    print(indicator_objs)
    print(alert)


def command():
    indicator_selection = [
        price(),
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
        allow_reentry=True,
    )
