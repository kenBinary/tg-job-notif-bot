import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
import re
from states.conversation_states import ConversationStates
from sqlalchemy.orm import sessionmaker
from db.models.User import User
from db.repository.user_repository import add_user, get_user_by_telegram_id, update_user

logger = logging.getLogger(__name__)


async def receive_keywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    SessionLocal: sessionmaker,
) -> int:
    chat_user = update.effective_user
    chat_id = update.effective_chat.id
    keywords_raw = update.message.text

    if not re.match(r"^[a-zA-Z0-9\s]+(?:,[a-zA-Z0-9\s]+)*$", keywords_raw.strip()):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid format. Please provide keywords separated by commas (e.g., 'python, react, remote').",
        )
        return ConversationStates.AWAITING_KEYWORDS

    keywords = [
        keyword.strip().lower()
        for keyword in keywords_raw.split(",")
        if keyword.strip()
    ]

    if not keywords:
        await context.bot.send_message(
            chat_id=chat_id,
            text="You didn't provide any valid keywords. Please try again.",
        )
        return ConversationStates.AWAITING_KEYWORDS

    user = User(
        telegram_id=str(chat_user.id),
        chat_id=str(chat_id),
        user_name=chat_user.username,
        first_name=chat_user.first_name,
        last_name=chat_user.last_name,
        language_bot=chat_user.language_code,
        is_bot=chat_user.is_bot,
        search_keywords=keywords_raw,
    )

    with SessionLocal() as session:
        existing_user = get_user_by_telegram_id(session, str(chat_user.id))
        if existing_user:
            update_user(
                session,
                existing_user.id,
                user_name=chat_user.username,
                chat_id=str(chat_id),
                first_name=chat_user.first_name,
                last_name=chat_user.last_name,
                language_bot=chat_user.language_code,
                is_bot=chat_user.is_bot,
                search_keywords=keywords_raw,
            )
            logger.info(f"Updated user {existing_user.id} with new keywords.")
        else:
            add_user(session, user)
            logger.info(f"Added new user with telegram_id {chat_user.id}.")
        session.commit()

    confirmation_message = (
        "Great! I've saved your keywords.\n"
        f"I will now notify you every 1 minute with new jobs matching: `{', '.join(keywords)}`.\n"
        "You can update your keywords anytime by stopping (/stop) and then starting (/start) again.\n"
        "You can also just /stop to unsubscribe from notifications."
    )
    await context.bot.send_message(chat_id=chat_id, text=confirmation_message)
    return ConversationHandler.END
