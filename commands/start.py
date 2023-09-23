from telegram import Update
from telegram.ext import CallbackContext


async def command(update: Update, context: CallbackContext) -> None:  # pylint: disable=unused-argument
    # pprint user
    await update.message.reply_text(
        """
👋 Welcome to Cryptocurrencies Alert Bot!

Stay ahead of the crypto market with our powerful features:
🔔 Custom Alerts: Set price & volume thresholds.
📈 Real-Time Data: Instant crypto market updates.
💼 Multi-Platform: Receive alerts on Telegram.
🤖 User-Friendly: Easy configuration & management.

Upgrade to our Premium Plan for unlimited alerts! 🚀

By default, you can create up to 5 alerts. To get started, simply type the /help command for instructions or /premium to learn more about our premium offering.

Happy trading! 📊💰
"""
    )
