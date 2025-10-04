import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repository.user_repository import get_user_by_chat_id

logger = logging.getLogger(__name__)


async def view_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        if not user:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You are not currently subscribed to job notifications. Send /start to subscribe and set keywords.",
            )
            return

        if not user.search_keywords:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You don't have any keywords set yet. Send /start to set your job search keywords.",
            )
            return

        keywords = [
            keyword.strip()
            for keyword in user.search_keywords.split(",")
            if keyword.strip()
        ]

        if not keywords:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You don't have any valid keywords set. Send /start to update your job search keywords.",
            )
            return

        keywords_display = "`, `".join(keywords)
        message = (
            f"Your current job search keywords are:\n`{keywords_display}`\n\n"
            f"I'm actively searching for jobs matching these keywords and will notify you when new ones are found.\n\n"
            f"To update your keywords, use /stop and then /start again. Or simply use /change to update them directly.\n"
        )

        await context.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Displayed keywords for user {user.telegram_id}")
