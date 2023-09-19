# Define conversation states
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

CRYPTO, TYPE, DIRECTION, VALUE, TIMES = range(5)


# Function to start the /create command
async def select_crypto(update: Update, context: CallbackContext) -> int:
    keyboard = [
        ["BTC", "ETH", "BNB"],
        ["ADA", "SOL", "DOT"],
    ]
    await update.message.reply_text(
        "Please select a cryptocurrency to set an alert for:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"),
    )

    return CRYPTO


async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    print(update.message.text)
    keyboard = [
        [
            InlineKeyboardButton("Price", callback_data="price"),
            InlineKeyboardButton("Volume", callback_data="volume"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose 'Price' or 'Volume':", reply_markup=reply_markup)

    return TYPE


async def select_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Goodbye!")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text("Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def command():
    return ConversationHandler(
        entry_points=[CommandHandler("create", select_crypto)],
        states={
            CRYPTO: [MessageHandler(filters.TEXT, select_type)],
            TYPE: [MessageHandler(filters.TEXT, select_direction)],
            # GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            # PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            # LOCATION: [
            #     MessageHandler(filters.LOCATION, location),
            #     CommandHandler("skip", skip_location),
            # ],
            # BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
