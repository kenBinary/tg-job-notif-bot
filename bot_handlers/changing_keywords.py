import logging
from db.repository.user_repository import get_user_by_chat_id, update_user
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from sqlalchemy.orm import sessionmaker
from states.conversation_states import ConversationStates

logger = logging.getLogger(__name__)


async def changing_keywords(
    update: Update, context: ContextTypes.DEFAULT_TYPE, SessionLocal: sessionmaker
) -> int:
    user = update.effective_user
    chat_id = update.effective_chat.id

    with SessionLocal() as session:
        user = get_user_by_chat_id(session, str(chat_id))
        if user:
            update_user(session, user.id, chat_id=None)
            logger.info(f"User {user.telegram_id} unsubscribed.")
            session.commit()
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You are not currently subscribed. Send /start to subscribe.",
            )
            return ConversationHandler.END

        message = (
            f"Hello, {user.first_name}! You are changing keywords, you've been unsubscribed in the meantime.\n\n"
            "Please provide a list of keywords for the jobs you're interested in separated by commas. \n"
            "For example: `python, react, virtual assistant`\n\n"
            "A maximum of 10 keywords is allowed, any additional keywords will be ignored.\n\n"
            "You can send /cancel at any time to stop this process."
        )
        await context.bot.send_message(chat_id=chat_id, text=message)

    return ConversationStates.AWAITING_KEYWORDS
