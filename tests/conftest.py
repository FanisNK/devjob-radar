import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.job import Job
from app.models.user import User


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


# Tell FastAPI to use the test database instead of the main database.
app.dependency_overrides[get_db] = override_get_db


# Create a test client for sending HTTP requests.
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# Create a test user before each test.
@pytest.fixture
def test_user():
    db = TestingSessionLocal()

    try:
        user = User(
            email="test@example.com",
            hashed_password=hash_password("TestPassword123"),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

    finally:
        db.close()



# Create a second test user.
@pytest.fixture
def second_user():
    db = TestingSessionLocal()

    try:
        user = User(
            email="second@example.com",
            hashed_password=hash_password("SecondPassword123"),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

    finally:
        db.rollback()
        db.close()



# Create an access token for the second test user.
@pytest.fixture
def second_user_auth_headers(second_user):
    access_token = create_access_token(
        data={"sub": str(second_user.id)}
    )

    return {"Authorization": f"Bearer {access_token}"}



# Create an access token for the test user.
@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(
        data={"sub": str(test_user.id)}
    )

    return {"Authorization": f"Bearer {access_token}"}


# Create a test client with authentication enabled.
@pytest.fixture
def authenticated_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


# Create a test job before a test and delete it after the test.
@pytest.fixture
def sample_job(test_user):
    db = TestingSessionLocal()

    try:
        job = Job(
            user_id=test_user.id,
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

        yield job

    finally:
        db.rollback()
        db.close()


# Clean the test database before and after each test.
@pytest.fixture(autouse=True)
def clean_test_database():
    with test_engine.begin() as connection:
        connection.execute(delete(Job))
        connection.execute(delete(User))

    yield

    with test_engine.begin() as connection:
        connection.execute(delete(Job))
        connection.execute(delete(User))
