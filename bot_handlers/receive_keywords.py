import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
import re
from states.conversation_states import ConversationStates
from db.models.User import User
from db.repository.user_repository import add_user, get_user_by_telegram_id, update_user

logger = logging.getLogger(__name__)


async def receive_keywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    SessionLocal = context.bot_data.get("SessionLocal")
    if not SessionLocal:
        logger.error("SessionLocal not found in bot_data")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred. Please try again later.",
        )
        return ConversationHandler.END

    chat_user = update.effective_user
    chat_id = update.effective_chat.id
    keywords_raw = update.message.text

    if not re.match(
        r"^[a-zA-Z0-9\s\-.]+(?:,[a-zA-Z0-9\s\-.]+)*$", keywords_raw.strip()
    ):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"Invalid format. Please provide keywords separated by commas (e.g., 'python, react, remote'). \n"
                f"The keywords can only contain letters, numbers, spaces, hyphens (-), and periods (.)"
            ),
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

    keywords = keywords[:10]
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
        f"I will now notify you periodically with new jobs matching: {', '.join(keywords)}.\n\n"
        "You can update your keywords anytime by stopping (/stop) and then starting (/start) again.\n"
        "Or you can just send /change to update your keywords.\n"
        "You may also send /view to see your current keywords.\n"
        "You can also send /stop to unsubscribe from notifications."
    )
    await context.bot.send_message(chat_id=chat_id, text=confirmation_message)
    return ConversationHandler.END
