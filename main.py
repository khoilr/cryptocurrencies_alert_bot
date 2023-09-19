import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackContext
from commands.start import command as start_command
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from commands.create import command as create_command

import telegram

load_dotenv()

# Define conversation states
CRYPTO, TYPE, DIRECTION, VALUE, TIMES = range(5)

# Initialize a dictionary to store user data during the conversation
user_data = {}


# Function to start the /create command
def start_create(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Bitcoin", callback_data="BTC"), InlineKeyboardButton("Ethereum", callback_data="ETH")],
        [
            InlineKeyboardButton("Binance Coin", callback_data="BNB"),
            InlineKeyboardButton("Cardano", callback_data="ADA"),
        ],
        [InlineKeyboardButton("Solana", callback_data="SOL")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a cryptocurrency to set an alert for:", reply_markup=reply_markup)

    return CRYPTO


# Function to handle cryptocurrency selection
def select_crypto(update: Update, context: CallbackContext) -> int:
    user_data["crypto"] = update.callback_query.data
    update.callback_query.message.edit_text(f"You selected {user_data['crypto']}. Choose 'Price' or 'Volume':")

    return TYPE


# Function to handle alert type (price or volume)
def select_type(update: Update, context: CallbackContext) -> int:
    user_data["type"] = update.message.text.lower()
    update.message.reply_text(
        f"You chose to set an alert based on {user_data['type']}."
        " Do you want to be alerted when the price goes up, down, or crosses a value?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Up", callback_data="up"),
                    InlineKeyboardButton("Down", callback_data="down"),
                    InlineKeyboardButton("Cross", callback_data="cross"),
                ]
            ]
        ),
    )

    return DIRECTION


# Function to handle alert direction (up, down, cross)
def select_direction(update: Update, context: CallbackContext) -> int:
    user_data["direction"] = update.callback_query.data
    update.callback_query.message.edit_text(
        f"You want to be alerted when the price {user_data['direction']}."
        " Enter the {user_data['type']} value at which to be alerted:"
    )

    return VALUE


# Function to handle value input
def select_value(update: Update, context: CallbackContext) -> int:
    user_data["value"] = update.message.text
    update.message.reply_text("How many times would you like to be alerted?")

    return TIMES


# Function to handle the final step and set up the alert
def set_alert(update: Update, context: CallbackContext) -> int:
    times = update.message.text
    # Process user data and set up the alert here
    # You can access user_data['crypto'], user_data['type'], user_data['direction'], user_data['value'], and 'times'
    # to set up the alert as per your requirements

    update.message.reply_text(
        f"Alert set for {user_data['crypto']} based on {user_data['type']} when price goes {user_data['direction']} "
        f"to {user_data['value']} value, to be triggered {times} times."
    )

    return ConversationHandler.END


# Function to handle the /cancel command
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Alert creation canceled.")
    return ConversationHandler.END


def main():
    # Init the application
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    # Add commands handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(create_command())
    # Long polling
    app.run_polling()

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("create", start_create)],
    #     states={
    #         CRYPTO: [MessageHandler(Filters.regex(r"^[A-Z]+$"), select_crypto)],
    #         TYPE: [MessageHandler(Filters.regex(r"^Price$|^Volume$"), select_type)],
    #         DIRECTION: [MessageHandler(Filters.regex(r"^up$|^down$|^cross$"), select_direction)],
    #         VALUE: [MessageHandler(Filters.text & ~Filters.command, select_value)],
    #         TIMES: [MessageHandler(Filters.text & ~Filters.command, set_alert)],
    #     },
    #     fallbacks=[CommandHandler("cancel", cancel)],
    # )

    # dp.add_handler(conv_handler)

    # add the /start command


if __name__ == "__main__":
    main()
