from datetime import datetime, timedelta
from logging import Logger
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from states.conversation_states import ConversationStates
from sqlalchemy.orm import sessionmaker
from db.repository.user_repository import get_user_by_telegram_id


# TODO: Finish implementing this
async def receive_keywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    logger: Logger,
    SessionLocal: sessionmaker,
) -> int:
    chat_user = update.effective_user
    chat_id = update.effective_chat.id

    with SessionLocal() as session:
        user = get_user_by_telegram_id(session, str(chat_user.id))

        if user is None:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Welcome! Please /start and  provide keywords separated by commas (e.g., 'python, react, remote') to start receiving job notifications.",
            )
            return ConversationStates.AWAITING_KEYWORDS

        last_active = datetime.strptime(user.last_active, "%Y-%m-%d %H:%M:%S")
        week_from_last_active = last_active + timedelta(weeks=1)
        current_time = datetime.now()
        days_left = (week_from_last_active - current_time).days
        active_message = (
            "You are currently active and subscribed from notifications.\n"
            f"You have {days_left} days left in your active period."
            f"Please /active before {week_from_last_active} to continue receiving notifications.\n"
        )
        if user.is_active:
            await context.bot.send_message(
                chat_id=chat_id,
                text=active_message,
            )
