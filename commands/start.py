"""
_summary_: Handles the /start command to provide users with a welcome message and bot information.
"""
from telegram import Update
from telegram.ext import CallbackContext


async def command(
    update: Update, context: CallbackContext
) -> None:  # pylint: disable=unused-argument
    """
    Handles the /start command to provide users with a welcome message and bot information.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.CallbackContext): The context object for handling callbacks.

    Returns:
        None
    """
    # Send a welcome message and introduce the bot's features to the user.
    effective_user = update.effective_user
    print(effective_user)
    print(update.message.from_user)
    await update.message.reply_text(
        """
👋 Welcome to Cryptocurrencies Alert Bot!

Stay ahead of the crypto market with our powerful features:
🔔 Custom Alerts: Set price & volume thresholds.
📈 Real-Time Data: Instant crypto market updates.
💼 Multi-Platform: Receive alerts on Telegram.
🤖 User-Friendly: Easy configuration & management.

By default, you can create up to 5 alerts. To get started, simply type the /help command for instructions or /premium to learn more about our premium offering.

Happy trading! 📊💰
"""
    )
