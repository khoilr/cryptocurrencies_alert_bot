from uuid import uuid4

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler

from bot.commands.create.constants import (
    CONDITION,
    COMPLETE,
    CONDITION_VALUE,
    CONDITION_VALUE_BY,
    CONDITION_VALUE_TWO,
    INTERVAL,
    KLINES,
    PRICE,
    conditions,
    intervals,
)
from bot.commands.create.advanced_filters import positive_number, two_positive_numbers, percentage_or_positive_number
from bot.commands.create.indicator import new_indicator
from bot.commands.create.indicators.operators.condition import input_condition, input_value
from bot.commands.create.indicators.operators.interval import input_klines, input_interval

CREATED_MESSAGE = "Indicator created"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_id = str(uuid4())
    context.user_data.setdefault("indicators", []).append({"name": "price", "id": current_id})
    context.user_data["current_id"] = str(current_id)
    return await input_condition(update, context)


async def condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    condition_id = update.callback_query.data
    condition_obj = next((_condition["name"] for _condition in conditions if _condition["id"] == condition_id), None)

    context.user_data["indicators"] = [
        {**indicator, "condition": condition_obj} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    return await input_value(update, context)


async def value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    indicators = context.user_data["indicators"]
    current_id = context.user_data["current_id"]
    value_value = update.message.text
    condition_value = next((indicator["condition"] for indicator in indicators if indicator["id"] == current_id), None)

    context.user_data["indicators"] = [
        {**indicator, "value": value_value} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    return (
        await input_interval(update, context)
        if condition_value in ["increase_by", "decrease_by"]
        else await new_indicator(update, context)
    )


async def interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interval_id = update.callback_query.data
    interval_obj = next((_interval["name"] for _interval in intervals if _interval["id"] == interval_id), None)

    context.user_data["indicators"] = [
        {**indicator, "interval": interval_obj} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    return await input_klines(update, context)


async def klines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    klines_input = update.message.text

    context.user_data["indicators"] = [
        {**indicator, "klines": klines_input} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    await update.message.reply_text(CREATED_MESSAGE)
    return await new_indicator(update, context)


def price():
    global interval, condition

    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern="^" + PRICE + "$")],
        states={
            CONDITION: [
                CallbackQueryHandler(
                    condition,
                    pattern="^(" + "|".join([condition["id"] for condition in conditions]) + ")$",
                )
            ],
            CONDITION_VALUE: [MessageHandler(positive_number, value)],
            CONDITION_VALUE_BY: [MessageHandler(percentage_or_positive_number, value)],
            CONDITION_VALUE_TWO: [MessageHandler(two_positive_numbers, value)],
            INTERVAL: [
                CallbackQueryHandler(
                    interval,
                    pattern="^(" + "|".join([interval["id"] for interval in intervals]) + ")$",
                )
            ],
            KLINES: [MessageHandler(positive_number, klines)],
        },
        fallbacks=[],
        map_to_parent={ConversationHandler.END: COMPLETE},
        allow_reentry=True,
    )
