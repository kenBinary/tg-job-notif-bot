import logging
from telegram.ext import (
    ContextTypes,
)

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    user = update.effective_user
    error_message = (
        f"Hello, {user.first_name}! an unexpected error has occured.\n\n"
        "Please retry your last action.\n\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)
