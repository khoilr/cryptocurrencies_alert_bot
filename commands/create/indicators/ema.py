# type: ignore
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
	CallbackQueryHandler,
	ContextTypes,
	ConversationHandler,
	MessageHandler,
	filters,
)

from commands.create.constants import (
	CONDITION,
	DECREASE_TO,
	EMA,
	ENTER_BOUND,
	EXIT_BOUND,
	INCREASE_TO,
	INTERVAL,
	REACH_TO,
	CONDITION_VALUE,
)
from commands.create.indicators.condition import input_condition, input_value
from commands.create.indicators.interval import input_interval

PERIOD, SOURCE = [str(uuid4()) for _ in range(2)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("indicators", []).append({"name": "ema"})

    keyboards = [
        [
            InlineKeyboardButton("Open", callback_data="open"),
            InlineKeyboardButton("High", callback_data="high"),
        ],
        [
            InlineKeyboardButton("Low", callback_data="low"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboards)

    await update.callback_query.edit_message_text("Choose source", reply_markup=reply_markup)

    return SOURCE


async def input_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source_input = update.callback_query.data
    # append to params in indicators where name is ema

    await update.callback_query.edit_message_text("Enter period")

    return PERIOD


async def period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period_input = update.message.text

    # Validate period is number and greater than 0
    try:
        period_input = int(period_input)
        if period_input <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid period. Please enter a number greater than 0")
        return PERIOD

    context.user_data["indicator"]["params"].append({"name": "period", "value": period_input})
    return await input_interval(update, context)


async def interval(update: Update, context=ContextTypes.DEFAULT_TYPE):
    interval_input = update.callback_query.data
    context.user_data["indicator"]["params"].append({"name": "interval", "value": interval_input})
    return await input_condition(update, context)


async def value(update: Update, context=ContextTypes.DEFAULT_TYPE):
    value_input = update.message.text

    # Validate period is number and greater than 0
    try:
        value_input = float(value_input)
    except ValueError:
        await update.message.reply_text("Invalid value. Please enter a number")
        return CONDITION_VALUE

    context.user_data["indicator"]["params"].append({"name": "value", "value": value_input})
    return await input_condition(update, context)


def ema():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern="^" + EMA + "$")],
        states={
            SOURCE: [CallbackQueryHandler(input_period, pattern="^(open|high|low|close)$")],
            PERIOD: [MessageHandler(~filters.COMMAND & filters.TEXT, period)],
            INTERVAL: [
                CallbackQueryHandler(
                    interval,
                    pattern="^(1m|3m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d|3d|1w|1M)$",
                )
            ],
            CONDITION: [
                CallbackQueryHandler(
                    input_value,
                    pattern=f"^({INCREASE_TO}|{DECREASE_TO}|{REACH_TO}|{ENTER_BOUND}|{EXIT_BOUND})$",
                )
            ],
            CONDITION_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, value)],
        },
        fallbacks=[],
        map_to_parent={CONDITION: CONDITION},
    )
