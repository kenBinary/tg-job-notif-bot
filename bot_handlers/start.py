from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from states.conversation_states import ConversationStates


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    welcome_message = (
        f"Hello, {user.first_name}! I'm a job notification bot.\n\n"
        "Please provide a list of keywords for the jobs you're interested in, separated by commas. "
        "For example: `python, react, remote`\n\n"
        "You can send /cancel at any time to stop this process."
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=welcome_message
    )
    return ConversationStates.AWAITING_KEYWORDS
