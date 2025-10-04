import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from db.repository.user_repository import get_user_by_chat_id, update_user

logger = logging.getLogger(__name__)


async def stop_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SessionLocal = context.bot_data.get("SessionLocal")
    if not SessionLocal:
        logger.error("SessionLocal not found in bot_data")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred. Please try again later.",
        )
        return

    chat_id = update.effective_chat.id
    with SessionLocal() as session:
        user = get_user_by_chat_id(session, str(chat_id))
        if user:
            update_user(session, user.id, chat_id=None)
            logger.info(f"User {user.telegram_id} unsubscribed.")
            await context.bot.send_message(
                chat_id=chat_id,
                text="You have been unsubscribed from job notifications. Send /start to subscribe again.",
            )
            session.commit()
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You are not currently subscribed. Send /start to subscribe.",
            )
