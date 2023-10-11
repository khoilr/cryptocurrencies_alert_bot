# type: ignore
from uuid import uuid4

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from commands.create.constants import (
    CONDITION,
    COMPLETE,
    CONDITION_VALUE,
    INTERVAL,
    KLINES,
    PRICE,
    conditions,
    intervals,
)
from commands.create.indicators.condition import input_condition, input_value
from commands.create.indicators.interval import input_interval, input_klines
from commands.create.indicator import new_indicator


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_id = str(uuid4())
    context.user_data.setdefault("indicators", []).append({"name": "price", "id": current_id})
    context.user_data["current_id"] = str(current_id)
    return await input_condition(update, context)


async def condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get condition object
    condition_id = update.callback_query.data
    condition_obj = next((condition["name"] for condition in conditions if condition["id"] == condition_id), None)

    # Update context
    context.user_data["indicators"] = [
        {**indicator, "condition": condition_obj} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    return await input_value(update, context)


async def value(update: Update, context=ContextTypes.DEFAULT_TYPE):
    value_input = update.message.text
    current_id = context.user_data["current_id"]
    indicators = context.user_data["indicators"]
    condition_value = next((indicator["condition"] for indicator in indicators if indicator["id"] == current_id), None)

    def update_user_data(this_value):
        nonlocal indicators
        indicators = [
            {**indicator, "value": this_value} if indicator["id"] == current_id else indicator
            for indicator in indicators
        ]
        context.user_data["indicators"] = indicators

    if condition_value in ["enter_bound", "exit_bound"]:
        value_input = value_input.split(",")
        if len(value_input) != 2:
            await update.message.reply_text("Invalid input. Please enter 2 values separated by a comma.")
            return await input_value(update, context)

        try:
            value_input = [float(value) for value in value_input]
            if value_input[0] >= value_input[1]:
                raise ValueError("The first value must be less than the second value.")
        except ValueError:
            await update.message.reply_text("Invalid input")
            return await input_value(update, context)

        update_user_data(value_input)
        await update.message.reply_text("Indicator created")
        return await new_indicator(update, context)

    try:
        value_input = float(value_input)
    except ValueError:
        await update.message.reply_text("Invalid value. Please enter a number.")
        return await input_value(update, context)

    update_user_data(value_input)

    if condition_value in ["increase_by", "decrease_by"]:
        await update.message.reply_text("Invalid value. Please enter a number.")
        return await input_interval(update, context)

    await update.message.reply_text("Indicator created")
    return await new_indicator(update, context)


async def interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interval_id = update.callback_query.data
    interval_obj = next((interval["name"] for interval in intervals if interval["id"] == interval_id), None)

    context.user_data["indicators"] = [
        {**indicator, "interval": interval_obj} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    return await input_klines(update, context)


async def klines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    klines_input = update.message.text

    try:
        klines_input = int(klines_input)
    except ValueError:
        await update.message.reply_text("Invalid value. Please enter a number")
        return await input_klines(update, context)

    if klines_input < 1:
        await update.message.reply_text("Invalid value. Please enter a number")
        return await input_klines(update, context)

    context.user_data["indicators"] = [
        {**indicator, "klines": klines_input} if indicator["id"] == context.user_data["current_id"] else indicator
        for indicator in context.user_data["indicators"]
    ]

    await update.message.reply_text("Indicator created")
    return await new_indicator(update, context)


def price():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern="^" + PRICE + "$")],
        states={
            CONDITION: [
                CallbackQueryHandler(
                    condition,
                    pattern="^(" + "|".join([condition["id"] for condition in conditions]) + ")$",
                )
            ],
            CONDITION_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, value)],
            INTERVAL: [
                CallbackQueryHandler(
                    interval,
                    pattern="^(" + "|".join([interval["id"] for interval in intervals]) + ")$",
                )
            ],
            KLINES: [MessageHandler(filters.TEXT & ~filters.COMMAND, klines)],
        },
        fallbacks=[],
        map_to_parent={ConversationHandler.END: COMPLETE},
    )
