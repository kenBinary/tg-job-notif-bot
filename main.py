from functools import partial
import os
import logging
from services.olj_jobs_api import OLJJobsAPIService
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from dotenv import load_dotenv
from bot_handlers.cancel import cancel
from bot_handlers.error_handler import error_handler
from db.engine.engine import engine_init_local, engine_init_remote
from db.session.session import create_session_factory
from states.conversation_states import ConversationStates
from bot_handlers.start import start
from bot_handlers.stop_notifications import stop_notifications
from bot_handlers.receive_keywords import receive_keywords
from bot_handlers.send_job_notification import send_job_notification
from utils.args_init import init_cli_args

logging.basicConfig(
    format="%(asctime)s [%(levelname)-8s]: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    args = init_cli_args()
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    olj_api = OLJJobsAPIService(API_BASE_URL)

    logger.info(f"Running in {'development' if args.dev else 'production'} mode")
    if olj_api.is_healthy():
        logger.info("API is healthy")
    else:
        raise RuntimeError("API is not healthy. Exiting.")

    TELEGRAM_BOT_TOKEN = os.environ.get(
        "TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    )
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "ERROR: Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot token."
        )
        return

    if args.prod:
        logger.info("Using remote database")
        engine = engine_init_remote()
    else:
        logger.info("Using local database")
        engine = engine_init_local()
    SessionLocal = create_session_factory(engine)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationStates.AWAITING_KEYWORDS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    partial(receive_keywords, SessionLocal=SessionLocal),
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.add_handler(
        CommandHandler(
            "stop",
            partial(stop_notifications, SessionLocal=SessionLocal),
        )
    )

    job_queue = application.job_queue
    job_queue.run_repeating(
        partial(
            send_job_notification,
            SessionLocal=SessionLocal,
            olj_api=olj_api,
        ),
        interval=60,
        first=10,
        name="send_job_notification",
    )

    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
