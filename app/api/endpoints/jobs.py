from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services import job_service


# Create a router for all job-related API endpoints.
router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


# Create a new job.
@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
):
    try:
        # Create a new job using the service layer.
        return job_service.create_job(db, job_data)

    except IntegrityError:
        # Return a conflict error if the job URL already exists.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job with this URL already exists",
        )


# Retrieve all available jobs.
@router.get("/", response_model=list[JobResponse])
def read_jobs(db: Session = Depends(get_db)):
    return job_service.get_jobs(db)


# Retrieve one job by its ID.
@router.get("/{job_id}", response_model=JobResponse)
def read_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = job_service.get_job_by_id(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


# Update an existing job by its ID.
@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobCreate,
    db: Session = Depends(get_db),
):
    # Find the job in the database.
    job = job_service.get_job_by_id(db, job_id)

    # Return an error if the job does not exist.
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    try:
        # Update the job with the new data.
        return job_service.update_job(db, job, job_data)

    except IntegrityError:
        # Return a conflict error if the job URL already exists.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job with this URL already exists",
        )


# Delete a job by its ID.
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = job_service.get_job_by_id(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job_service.delete_job(db, job)