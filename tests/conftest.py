import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.job import Job


# Load test database settings from the .env.test file.
load_dotenv(".env.test", override=True)

# Get the test database URL from environment variables.
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# Make sure the test database URL is configured.
if not TEST_DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured in .env.test")

# Create a separate engine for the test database.
test_engine = create_engine(TEST_DATABASE_URL)

# Create a factory for test database sessions.
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


# Override the application's database dependency during tests.
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# Create all database tables before running tests.
Base.metadata.create_all(bind=test_engine)

# Tell FastAPI to use the test database instead of the main database.
app.dependency_overrides[get_db] = override_get_db


# Create a test client for sending HTTP requests.
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# Create a test job before a test and delete it after the test.
@pytest.fixture
def sample_job():
    db = TestingSessionLocal()

    try:
        # Create a test job with sample data.
        job = Job(
            title="Test Python Developer",
            company="Test Company",
            description="A test job description",
            salary_min=2000,
            salary_max=3000,
            url="https://example.com/jobs/test-python-developer",
        )

        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id

        yield job

    finally:
      # Delete the test job if it still exists in the database.
      if "job_id" in locals():
        db.rollback()
        db.execute(delete(Job).where(Job.id == job_id))
        db.commit()

      db.close()


# Clean the test database before and after each test.
@pytest.fixture(autouse=True)
def clean_test_database():
    # Remove existing test jobs before the test starts.
    with test_engine.begin() as connection:
        connection.execute(delete(Job))

    yield

    # Remove all test jobs after the test finishes.
    with test_engine.begin() as connection:
        connection.execute(delete(Job))
