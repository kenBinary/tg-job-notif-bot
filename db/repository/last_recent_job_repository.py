from db.models.LastRecentJob import LastRecentJob


def get_last_recent_job(session) -> LastRecentJob | None:
    return session.query(LastRecentJob).first()


def update_last_recent_job(session, last_recent_job_id: int) -> LastRecentJob | None:
    last_recent_job = session.query(LastRecentJob).first()
    if last_recent_job:
        last_recent_job.last_recent_job_id = last_recent_job_id
    return last_recent_job
