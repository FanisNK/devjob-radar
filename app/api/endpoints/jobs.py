from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services import job_service
from app.core.security import get_current_user
from app.models.user import User

# Create a router for all job-related API endpoints.
router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


# Create a new job.

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return job_service.create_job(
            db,
            job_data,
            user_id=current_user.id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job with this URL already exists",
        )


# Retrieve jobs belonging to the current user with pagination.
@router.get("/", response_model=list[JobResponse])
def read_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return job_service.get_jobs(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


# Retrieve one job belonging to the current user.
@router.get("/{job_id}", response_model=JobResponse)
def read_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = job_service.get_job_by_id(
        db,
        job_id,
        user_id=current_user.id,
    )

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
    current_user: User = Depends(get_current_user),
):
    # Find the job in the database.
    job = job_service.get_job_by_id(
        db,
        job_id,
        user_id=current_user.id,
    )

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
    current_user: User = Depends(get_current_user),
):
    job = job_service.get_job_by_id(
        db,
        job_id,
        user_id=current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job_service.delete_job(db, job)
