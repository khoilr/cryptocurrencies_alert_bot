# type: ignore
"""Input Indicator State"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.commands.create.constants import INDICATOR, PAGINATION_LIMIT, indicators, input_indicator_message, COMPLETE


async def input_indicator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pagination_offset = context.user_data["pagination_offset"]

    pagination = []
    if pagination_offset > 0:
        pagination.append(InlineKeyboardButton("⏪ Previous", callback_data="previous"))
    if (pagination_offset + 1) * PAGINATION_LIMIT < len(indicators):
        pagination.append(InlineKeyboardButton("⏩ Next", callback_data="next"))

    keyboards = [
        *[
            [InlineKeyboardButton(indicator["display_name"], callback_data=indicator["id"])]
            for indicator in indicators[
                PAGINATION_LIMIT * pagination_offset : PAGINATION_LIMIT * (pagination_offset + 1)
            ]
        ],
        pagination,
    ]

    reply_markup = InlineKeyboardMarkup(keyboards)

    if update.callback_query:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(input_indicator_message, reply_markup=reply_markup)

    return INDICATOR


async def next_button(update: Update, context=ContextTypes.DEFAULT_TYPE):
    context.user_data["pagination_offset"] += 1
    return await input_indicator(update, context)


async def previous_button(update: Update, context=ContextTypes.DEFAULT_TYPE):
    context.user_data["pagination_offset"] -= 1
    return await input_indicator(update, context)


# pylint: disable=unused-argument
async def new_indicator(update: Update, context=ContextTypes.DEFAULT_TYPE):
    keyboards = [
        [InlineKeyboardButton("Done", callback_data=COMPLETE)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboards)

    if update.callback_query:
        await update.callback_query.edit_message_text(text="Created indicator", reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(text="Created indicator", reply_markup=reply_markup)

    return ConversationHandler.END
