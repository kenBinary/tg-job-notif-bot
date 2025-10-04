import logging
from http import HTTPStatus
from fastapi import FastAPI, Response
from telegram.ext import Application
from bot import JobNotificationTrigger

logger = logging.getLogger(__name__)


def create_webhook_app(application: Application) -> FastAPI:
    logger.info("Creating webhook API...")

    app = FastAPI()

    @app.post("/webhook/trigger")
    async def trigger_job_notification() -> Response:
        try:
            await application.update_queue.put(JobNotificationTrigger())
            logger.info("JobNotificationTrigger added to update queue")
            return Response(
                status_code=HTTPStatus.OK, content="Job notification triggered"
            )
        except Exception as e:
            logger.error(f"Error triggering job notification: {e}", exc_info=True)
            return Response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=f"Error: {str(e)}"
            )

    @app.get("/health")
    async def health_check() -> dict:
        return {"status": "healthy"}

    logger.info("Webhook API created successfully")
    return app
