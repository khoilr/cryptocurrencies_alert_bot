from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.commands.create.constants import (
    CONDITION,
    CONDITION_VALUE,
    CONDITION_VALUE_BY,
    CONDITION_VALUE_TWO,
    conditions,
)
from bot.commands.create.constants import (
    input_condition_message,
    input_value_message,
    input_value_percentage_message,
    input_two_values_message,
)


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
            text=input_condition_message,
            reply_markup=reply_markup,
        )
    else:
        await update.effective_message.reply_text(
            text=input_condition_message,
            reply_markup=reply_markup,
        )

    return CONDITION


async def input_value(update: Update, context=ContextTypes.DEFAULT_TYPE):
    current_id = context.user_data["current_id"]
    indicators = context.user_data["indicators"]
    condition = next((indicator["condition"] for indicator in indicators if indicator["id"] == current_id), None)
    message = input_value_message

    if condition in ["increase_by", "decrease_by"]:
        message = input_value_percentage_message
    elif condition in ["enter_bound", "exit_bound"]:
        message = input_two_values_message

    if update.callback_query:
        await update.callback_query.edit_message_text(message)
    else:
        await update.effective_message.reply_text(message)

    if condition in ["enter_bound", "exit_bound"]:
        return CONDITION_VALUE_TWO
    elif condition in ["increase_by", "decrease_by"]:
        return CONDITION_VALUE_BY
    else:
        return CONDITION_VALUE
