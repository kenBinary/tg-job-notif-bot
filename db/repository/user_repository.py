from db.models.User import User


def add_user(session, user: User):
    session.add(user)


def get_user_by_id(session, user_id: int) -> User | None:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_chat_id(session, chat_id: str) -> User | None:
    return session.query(User).filter(User.chat_id == chat_id).first()


def get_user_by_telegram_id(session, telegram_id: str) -> User | None:
    return session.query(User).filter(User.telegram_id == telegram_id).first()


def get_all_users(session) -> list[User]:
    return session.query(User).filter(User.chat_id != None).all()


def update_user(session, user_id: int, **kwargs):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
    return user


def delete_user(session, user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        user.status = False
    return user
