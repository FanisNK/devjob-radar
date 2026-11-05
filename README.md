# DevJob Radar

A REST API for managing and tracking developer job opportunities, built with Python and FastAPI.

## Project Overview

DevJob Radar is a backend application designed to store, manage, and track developer job listings.

The project demonstrates backend development fundamentals, including REST API design, database integration, data validation, error handling, database migrations, and automated testing.

## Tech Stack

- **Python**
- **FastAPI** — REST API framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM (Object-Relational Mapping)
- **Alembic** — database migrations
- **Pydantic** — data validation and settings management
- **Pytest** — automated testing

## Features

- Create, retrieve, update, and delete job listings (CRUD).
- Validate job data using Pydantic.
- Prevent duplicate job URLs.
- Validate salary ranges.
- Handle missing resources with appropriate HTTP status codes.
- Manage database schema with Alembic migrations.
- Test API endpoints using Pytest and FastAPI TestClient.

## Project Structure

```text
MyDevjob_radar/
├── app/
│   ├── api/
│   │   └── endpoints/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── migrations/
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_jobs.py
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd MyDevjob_radar
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update `DATABASE_URL` in `.env` with your PostgreSQL connection string.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Running Tests

Configure a separate test database using `.env.test`, then run:

```bash
pytest
```

The test suite covers API endpoints, data validation, and error handling.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/jobs/` | Create a job listing |
| GET | `/api/v1/jobs/` | Retrieve all job listings |
| GET | `/api/v1/jobs/{job_id}` | Retrieve a job by ID |
| PUT | `/api/v1/jobs/{job_id}` | Update a job listing |
| DELETE | `/api/v1/jobs/{job_id}` | Delete a job listing |

## Project Status

The project is under active development. New features and improvements will be added over time.