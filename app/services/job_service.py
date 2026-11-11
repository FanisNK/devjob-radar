from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate


# Create a new job in the database.
# The function receives validated data and the owner's ID.
def create_job(
    db: Session,
    job_data: JobCreate,
    user_id: int,
) -> Job:
    new_job = Job(
        user_id=user_id,
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        url=job_data.url,
    )

    # Add the new job to the current database session.
    db.add(new_job)

    try:
        # Save the changes permanently in the database.
        db.commit()

    except IntegrityError:
        # Roll back the failed transaction.
        db.rollback()

        # Pass the database error to the API layer.
        raise

    # Refresh the object to load database-generated values.
    db.refresh(new_job)

    return new_job



# Retrieve jobs belonging to a specific user with pagination.
# The newest jobs will appear first.
def get_jobs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
) -> list[Job]:
    statement = (
        select(Job)
        .where(Job.user_id == user_id)
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = db.execute(statement)

    return list(result.scalars().all())



# Retrieve a job belonging to a specific user.
# Return None if the job does not exist or belongs to another user.
def get_job_by_id(
    db: Session,
    job_id: int,
    user_id: int,
) -> Job | None:
    statement = select(Job).where(
        Job.id == job_id,
        Job.user_id == user_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


# Update an existing job in the database.
# The function replaces the job data with the new validated data.
def update_job(
    db: Session,
    job: Job,
    job_data: JobCreate,
) -> Job:

    # Update the job fields with the new values.
    job.title = job_data.title
    job.company = job_data.company
    job.description = job_data.description
    job.salary_min = job_data.salary_min
    job.salary_max = job_data.salary_max
    job.url = job_data.url

    try:
        # Save the changes permanently in the database.
        db.commit()

    except IntegrityError:
        # Roll back the failed transaction.
        db.rollback()

        # Pass the database error to the API layer.
        raise

    # Refresh the object to get the latest database values.
    db.refresh(job)

    return job


# Delete a job from the database.
# Return True if the job was found and deleted.
def delete_job(db: Session, job: Job) -> bool:
    db.delete(job)
    db.commit()

    return True
