from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# Create a database engine.
# It manages connections between our application and PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)


# Create a factory for database sessions.
# Each session allows us to perform database operations.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Define a base class for all database models.
# Every model will inherit from this class.
class Base(DeclarativeBase):
    pass


# Provide a database session to an API endpoint.
# Always close the session after the request is completed.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
