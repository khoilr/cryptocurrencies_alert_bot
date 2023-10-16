# type: ignore
# pylint: disable=unused-argument
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.commands.create.constants import CONDITION, CONDITION_VALUE, conditions


async def input_condition(update: Update, context=ContextTypes.DEFAULT_TYPE):
    keyboards = [
        [
            InlineKeyboardButton(condition["display_name"], callback_data=condition["id"])
            for condition in conditions[i : i + 2]
        ]
        for i in range(0, len(conditions), 2)
    ]
    reply_markup = InlineKeyboardMarkup(keyboards)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="Input Condition",
            reply_markup=reply_markup,
        )
    else:
        await update.effective_message.reply_text(
            text="Input Condition",
            reply_markup=reply_markup,
        )

    return CONDITION


async def input_value(update: Update, context=ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text("Enter value")
    else:
        await update.effective_message.reply_text("Enter value")

    return CONDITION_VALUE
