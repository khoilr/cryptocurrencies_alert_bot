from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from bot.commands.pairs.constants import (
    PAGINATION,
    list_of_pairs_message,
    supported_pair_message,
    unsupported_pair_message,
)
from redis_connection import redis_client

load_dotenv()

NUM_ROWS = 4
NUM_COLS = 3
PAGINATION_LIMIT = NUM_ROWS * NUM_COLS

cryptos = redis_client.zrange("cryptos", 0, -1, desc=True)


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offset = context.user_data.setdefault("offset", 0)
    start_index = offset * PAGINATION_LIMIT
    end_index = (offset + 1) * PAGINATION_LIMIT

    pagination = []
    if offset > 0:
        pagination.append(InlineKeyboardButton("⏪ Previous", callback_data="previous"))
    if end_index < len(cryptos):
        pagination.append(InlineKeyboardButton("⏩ Next", callback_data="next"))

    keyboards = [
        [InlineKeyboardButton(crypto, callback_data=crypto) for crypto in cryptos[i : i + NUM_COLS]]
        for i in range(start_index, end_index, NUM_COLS)
    ]
    keyboards.append(pagination)
    reply_markup = InlineKeyboardMarkup(keyboards)

    if update.callback_query:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(list_of_pairs_message, reply_markup=reply_markup)

    return PAGINATION


async def next_button(update: Update, context=ContextTypes.DEFAULT_TYPE):
    context.user_data["offset"] += 1
    return await pairs(update, context)


async def previous_button(update: Update, context=ContextTypes.DEFAULT_TYPE):
    context.user_data["offset"] -= 1
    return await pairs(update, context)


async def check_pair(update: Update, context=ContextTypes.DEFAULT_TYPE):
    crypto = context.args[0].upper()
    if not redis_client.zscore("cryptos", crypto):
        await update.effective_message.reply_text(unsupported_pair_message)
    else:
        await update.effective_message.reply_text(supported_pair_message)

    return ConversationHandler.END


def command():
    return ConversationHandler(
        entry_points=[
            CommandHandler("pairs", check_pair, has_args=True),
            CommandHandler("pairs", pairs),
        ],
        states={
            PAGINATION: [
                CallbackQueryHandler(next_button, pattern="next"),
                CallbackQueryHandler(previous_button, pattern="previous"),
            ],
        },
        fallbacks=[],
        allow_reentry=True,
    )
