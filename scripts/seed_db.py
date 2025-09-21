from db.engine.engine import engine_init_local, engine_init_remote
from db.session.session import create_session_factory
from db.models.LastRecentJob import LastRecentJob
from utils.args_init import init_cli_args


def main():
    args = init_cli_args()
    if args.prod:
        print("Using remote database")
        engine = engine_init_remote()
    else:
        print("Using local database")
        engine = engine_init_local()

    SessionLocal = create_session_factory(engine)
    with SessionLocal() as session:
        existing_entry = session.query(LastRecentJob).first()
        if existing_entry:
            print("Database already seeded. Exiting.")
            return
        else:
            print("Seeding database...")
            last_recent_job = LastRecentJob(last_recent_job_id=None)
            session.add(last_recent_job)
            session.commit()
            print("Database seeded successfully!")


if __name__ == "__main__":
    main()
