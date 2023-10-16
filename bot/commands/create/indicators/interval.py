# type: ignore
# pylint: disable=unused-argument
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.commands.create.constants import INTERVAL, KLINES, intervals


async def input_interval(update: Update, context=ContextTypes.DEFAULT_TYPE):  # pylint: disable=unused-argument
    keyboards = [
        [InlineKeyboardButton(interval["display_name"], callback_data=interval["id"]) for interval in intervals[:5]],
        [InlineKeyboardButton(interval["display_name"], callback_data=interval["id"]) for interval in intervals[5:12]],
        [InlineKeyboardButton(interval["display_name"], callback_data=interval["id"]) for interval in intervals[12:]],
    ]
    reply_markup = InlineKeyboardMarkup(keyboards)

    if update.callback_query:
        await update.callback_query.edit_message_text(text="Input Interval", reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(text="Input Interval", reply_markup=reply_markup)

    return INTERVAL


async def input_klines(update: Update, context=ContextTypes.DEFAULT_TYPE):  # pylint: disable=unused-argument
    if update.callback_query:
        await update.callback_query.edit_message_text("Input number of klines")
    else:
        await update.effective_message.reply_text("Input number of klines")
    return KLINES
