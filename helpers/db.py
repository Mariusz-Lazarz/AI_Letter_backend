from sqlmodel import select
from models.user import User
from fastapi import HTTPException


def get_user_by_email(session, user):
    statement = select(User).where(User.email == user["email"])
    db_user = session.exec(statement).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
