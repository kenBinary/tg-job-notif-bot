import asyncio
import logging
from telegram.ext import (
    ContextTypes,
)
from sqlalchemy.orm import sessionmaker
from db.repository.user_repository import get_all_users
from services.olj_jobs_api import OLJJobsAPIService

logger = logging.getLogger(__name__)


async def send_job_notification(
    context: ContextTypes.DEFAULT_TYPE,
    SessionLocal: sessionmaker,
    olj_api: OLJJobsAPIService,
):
    with SessionLocal() as session:
        users = get_all_users(session)

        if not users:
            return

        logger.info(f"Sending job notifications to {len(users)} users.")
        for user in users:
            new_jobs_response, last_recent_job_id = olj_api.get_new_jobs(
                user.last_recent_job_id,
                q=user.search_keywords,
                limit=30,
            )
            user.last_recent_job_id = last_recent_job_id
            if not new_jobs_response.jobs:
                logger.info(f"No new jobs found. for user {user.telegram_id}")
                continue

            jobs = new_jobs_response.jobs
            for index, job in enumerate(jobs):
                delay = index * 1.5
                schedule_delayed_message(context, user.chat_id, job.summary, delay)
            logger.info(f"Sent {len(jobs)} new jobs to user {user.telegram_id}")
        logger.info(f"Finished sending job notifications to users.")

        session.commit()


def schedule_delayed_message(context, chat_id, message, delay):
    async def task():
        try:
            await send_message(context, chat_id, message, delay)
        except Exception as e:
            logger.error(f"Failed to send delayed message to {chat_id}: {e}")

    asyncio.create_task(task())


async def send_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: str,
    message: str,
    delay: int = 0,
):
    try:
        if delay > 0:
            await asyncio.sleep(delay)
        await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Failed to send message to {chat_id}: {e}")
