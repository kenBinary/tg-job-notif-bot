import asyncio
import logging
from typing import List, Tuple
from telegram.ext import (
    ContextTypes,
)
from sqlalchemy.orm import sessionmaker
from db.repository.user_repository import get_all_users
from dto.olj_scraper_api_dto import Job
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

        exclude_fields = ["job_overview", "raw_text"]
        logger.info(f"Sending job notifications to {len(users)} users.")

        recent_jobs: List[Job] = olj_api.get_new_jobs(
            limit=30, exclude=",".join(exclude_fields)
        ).jobs

        for user in users:
            if user.chat_id is None or user.search_keywords is None:
                logger.info(
                    f"Skipping user {user.telegram_id} due to missing chat_id or search_keywords."
                )
                continue

            new_jobs, last_recent_job_id = filter_jobs(
                recent_jobs, user.search_keywords, user.last_recent_job_id
            )
            user.last_recent_job_id = last_recent_job_id
            if not new_jobs:
                logger.info(f"No new jobs found. for user {user.telegram_id}")
                continue

            jobs = new_jobs
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


def filter_jobs(
    all_jobs: List[Job], user_keywords: List[str], last_seen_job_id: int
) -> Tuple[List[Job], int]:
    unseen_jobs = []

    for keyword in user_keywords:
        keyword_lower = keyword.lower()
        all_jobs = [
            job
            for job in all_jobs
            if keyword_lower in job.title.lower()
            or keyword_lower in job.summary.lower()
        ]

    for job in all_jobs:
        if job.id > last_seen_job_id:
            unseen_jobs.append(job)
        else:
            break
    return (unseen_jobs, unseen_jobs[0].id if unseen_jobs else last_seen_job_id)
