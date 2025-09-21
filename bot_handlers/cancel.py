from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Subscription process cancelled. You can start over by sending /start."
    )
    return ConversationHandler.END
