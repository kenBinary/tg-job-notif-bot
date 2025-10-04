import logging
from dataclasses import dataclass
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    TypeHandler,
    CallbackContext,
)
from bot_handlers.cancel import cancel
from bot_handlers.error_handler import error_handler
from states.conversation_states import ConversationStates
from bot_handlers.start import start
from bot_handlers.stop_notifications import stop_notifications
from bot_handlers.receive_keywords import receive_keywords
from bot_handlers.send_job_notification import send_job_notification
from bot_handlers.view_keywords import view_keywords
from bot_handlers.changing_keywords import changing_keywords

logger = logging.getLogger(__name__)


@dataclass
class JobNotificationTrigger:
    pass


async def handle_webhook_trigger(
    update: JobNotificationTrigger, context: CallbackContext
) -> None:
    logger.info("Webhook trigger received - sending job notifications")
    SessionLocal = context.bot_data.get("SessionLocal")
    olj_api = context.bot_data.get("olj_api")

    if not SessionLocal or not olj_api:
        logger.error("SessionLocal or olj_api not found in bot_data")
        return

    await send_job_notification(context, SessionLocal=SessionLocal, olj_api=olj_api)


def create_bot_application(telegram_token: str, SessionLocal, olj_api) -> Application:
    logger.info("Creating bot application...")

    application = ApplicationBuilder().token(telegram_token).build()

    application.bot_data["SessionLocal"] = SessionLocal
    application.bot_data["olj_api"] = olj_api

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationStates.AWAITING_KEYWORDS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_keywords,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    change_keywords_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("change", changing_keywords)],
        states={
            ConversationStates.AWAITING_KEYWORDS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_keywords,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(change_keywords_conv_handler)

    application.add_handler(
        CommandHandler(
            "stop",
            stop_notifications,
        )
    )
    application.add_handler(
        CommandHandler(
            "view",
            view_keywords,
        )
    )

    application.add_handler(
        TypeHandler(type=JobNotificationTrigger, callback=handle_webhook_trigger)
    )

    application.add_error_handler(error_handler)

    logger.info("Bot application created successfully")
    return application
