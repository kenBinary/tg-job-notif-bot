import asyncio
import os
import logging
import uvicorn
from dotenv import load_dotenv
from services.olj_jobs_api import OLJJobsAPIService
from db.engine.engine import engine_init_local, engine_init_remote
from db.session.session import create_session_factory
from utils.args_init import init_cli_args
from bot import create_bot_application
from webhook_api import create_webhook_app

logging.basicConfig(
    format="%(asctime)s [%(levelname)-8s]: %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main() -> None:
    load_dotenv()
    args = init_cli_args()
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))

    logger.info(f"Running in {'development' if args.dev else 'production'} mode")

    olj_api = OLJJobsAPIService(API_BASE_URL)
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

    application = create_bot_application(TELEGRAM_BOT_TOKEN, SessionLocal, olj_api)

    webhook_app = create_webhook_app(application)

    config = uvicorn.Config(
        app=webhook_app,
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)

    logger.info(f"Starting webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    logger.info("Starting Telegram bot with polling...")

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        await server.serve()

        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
