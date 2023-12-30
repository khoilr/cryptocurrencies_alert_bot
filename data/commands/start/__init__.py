from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from database.models.dao.user import User as User_DAO

message = """
🚀 Welcome to Cryptocurrencies Alert Bot! 🚀

Stay ahead in the crypto market with real-time alerts for various indicators, such as 📈 price, 📊 volume, 🔮 EMA, \
and more!

To get started, use /create to set up your alerts, or /alerts to see your current ones. \
For the current price of a specific cryptocurrency, just type /price <Crypto Pair> (e.g. /price BTCUSDT). \
Need a hand? Just type /help. 💬

Remember, crypto markets can be as volatile as a 🎢 roller coaster. Trade responsibly and do your research. 📚

With Cryptocurrencies Alert Bot, you'll never miss important crypto opportunities! 💰

Happy trading! 🌟🚀📆
"""


async def command(update: Update, context: CallbackContext) -> None:
    # Get user info
    effective_user = update.effective_user

    # Insert or update user
    user = User_DAO.upsert(**effective_user.to_dict())

    # Log
    logger.info(f"User {user.id} started the conversation.")

    # Reply
    await update.message.reply_text(message)
