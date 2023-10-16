from uuid import uuid4

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from bot.commands.create.constants import (
    CONDITION,
    COMPLETE,
    CONDITION_VALUE,
    INTERVAL,
    KLINES,
    PRICE,
    conditions,
    intervals,
)
from bot.commands.create.indicator import new_indicator
from bot.commands.create.indicators.condition import input_condition, input_value
from bot.commands.create.indicators.interval import input_interval, input_klines

CREATED_MESSAGE = "Indicator created"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_id = str(uuid4())
    context.user_data.setdefault("indicators", []).append({"name": "price", "id": current_id})
    context.user_data["current_id"] = str(current_id)
    return await input_condition(update, context)


async def condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get _condition object
    condition_id = update.callback_query.data
    condition_obj = next((_condition["name"] for _condition in conditions if _condition["id"] == condition_id), None)

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

    async def handle_invalid_input(error_message):
        await update.message.reply_text(error_message)
        return await input_value(update, context)

    try:
        if condition_value in ["enter_bound", "exit_bound"]:
            value_input = value_input.split(",")
            if len(value_input) != 2:
                return await handle_invalid_input("Invalid input. Please enter 2 values separated by a comma.")

            value_input = [float(_value) for _value in value_input]
            if value_input[0] >= value_input[1]:
                raise ValueError("The first value must be less than the second value.")

        elif condition_value in ["increase_by", "decrease_by"]:
            if value_input.endswith("%"):
                value_input = value_input[:-1]
                value_input = float(value_input)
                value_input = f"{value_input}%"
            else:
                value_input = float(value_input)

        else:
            value_input = float(value_input)

        update_user_data(value_input)
        await update.message.reply_text(CREATED_MESSAGE)

        return (
            await input_interval(update, context)
            if condition_value in ["enter_bound", "exit_bound"]
            else await new_indicator(update, context)
        )

    except ValueError:
        return await handle_invalid_input("Invalid input. Please enter a valid value.")


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
        allow_reentry=True,
    )
