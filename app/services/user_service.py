from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    # Find a user by email.
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def create_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    # Hash the password before saving it.
    hashed_password = hash_password(password)

    # Create a new user instance.
    db_user = User(
        email=email,
        hashed_password=hashed_password,
    )

    db.add(db_user)

    try:
        # Save the new user to the database.
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        # Roll back the transaction if the email already exists.
        db.rollback()
        raise

    return db_user