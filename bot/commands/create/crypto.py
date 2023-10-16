"""Input Crypto State"""
import os

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.commands.create.constants import CRYPTO, input_crypto_message, input_crypto_again_message
from bot.commands.create.indicator import input_indicator

load_dotenv()

# Environment variables
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Initialize a Redis connection
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)

# query top 6 cryptos from sorted set
top_cryptos = redis_client.zrange(
    "cryptos",
    0,
    5,
    desc=True,
)
top_cryptos = [
    [crypto.decode("utf-8") for crypto in top_cryptos[:3]],
    [crypto.decode("utf-8") for crypto in top_cryptos[3:]],
]

# Create a reply keyboard markup with the cryptocurrency options
reply_markup = ReplyKeyboardMarkup(top_cryptos, resize_keyboard=True, one_time_keyboard=True)


# Start command handler
async def input_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user to input cryptocurrency"""
    await update.message.reply_text(input_crypto_message, reply_markup=reply_markup)
    return CRYPTO


async def input_crypto_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user to input cryptocurrency again"""
    await update.message.reply_text(input_crypto_again_message, reply_markup=reply_markup)
    return CRYPTO


async def validate_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validate the cryptocurrency input"""
    # Get the user's input
    crypto = update.message.text

    # Check if the input is a valid cryptocurrency
    if not redis_client.zscore("cryptos", crypto):
        return await input_crypto_again(update, context)

    # Save the cryptocurrency in the user data for later use
    context.user_data["cryptos"] = [crypto]

    return await input_indicator(update, context)
