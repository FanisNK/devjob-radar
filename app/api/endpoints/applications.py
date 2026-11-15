from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import application_service
from app.schemas.application import (
  ApplicationCreate,
  ApplicationResponse,
  ApplicationUpdate,
)

router = APIRouter(
  prefix="/applications",
  tags=["Applications"],
)


@router.post(
  "/",
  response_model=ApplicationResponse,
  status_code=status.HTTP_201_CREATED,
)
def create_application_endpoint(
        application_data: ApplicationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
  try:
    return application_service.create_application(
      db=db,
      application_data=application_data,
      user_id=current_user.id,
    )
  except IntegrityError:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Application already exists or job does not exist",
    )


@router.get(
  "/",
  response_model=list[ApplicationResponse],
)
def get_applications_endpoint(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
  return application_service.get_applications(
    db=db,
    user_id=current_user.id,
    skip=skip,
    limit=limit,
  )


@router.get(
  "/{application_id}",
  response_model=ApplicationResponse,
)
def get_application_endpoint(
        application_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
  application = application_service.get_application_by_id(
    db=db,
    application_id=application_id,
    user_id=current_user.id,
  )

  if application is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Application not found",
    )

  return application


@router.put(
  "/{application_id}",
  response_model=ApplicationResponse,
)
def update_application_endpoint(
        application_id: int,
        application_data: ApplicationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
  application = application_service.get_application_by_id(
    db=db,
    application_id=application_id,
    user_id=current_user.id,
  )

  if application is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Application not found",
    )

  return application_service.update_application(
    db=db,
    application=application,
    application_data=application_data,
  )


@router.delete(
  "/{application_id}",
  status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application_endpoint(
        application_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
  application = application_service.get_application_by_id(
    db=db,
    application_id=application_id,
    user_id=current_user.id,
  )

  if application is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Application not found",
    )

  application_service.delete_application(
    db=db,
    application=application,
  )
