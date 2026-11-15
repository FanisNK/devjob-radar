from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def create_application(
        db: Session,
        application_data: ApplicationCreate,
        user_id: int,
) -> Application:
  # Create a new application object.
  new_application = Application(
    user_id=user_id,
    job_id=application_data.job_id,
    notes=application_data.notes,
  )

  # Add the application to the database session.
  db.add(new_application)

  try:
    # Save the application to the database.
    db.commit()

    # Refresh the object with database-generated values.
    db.refresh(new_application)

  except IntegrityError:
    # Roll back the transaction if a database error occurs.
    db.rollback()
    raise

  return new_application


def get_applications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
) -> list[Application]:
  # Retrieve applications belonging to a specific user.
  statement = (
    select(Application)
    .where(Application.user_id == user_id)
    .order_by(Application.created_at.desc())
    .offset(skip)
    .limit(limit)
  )

  result = db.execute(statement)

  return list(result.scalars().all())


def get_application_by_id(
        db: Session,
        application_id: int,
        user_id: int,
) -> Application | None:
  # Retrieve an application belonging to a specific user.
  statement = select(Application).where(
    Application.id == application_id,
    Application.user_id == user_id,
  )

  result = db.execute(statement)

  return result.scalar_one_or_none()


def update_application(
        db: Session,
        application: Application,
        application_data: ApplicationUpdate,
) -> Application:
  # Get only the fields provided in the request.
  update_data = application_data.model_dump(exclude_unset=True)

  # Update the application fields.
  for field, value in update_data.items():
    if value is not None or field == "notes":
      setattr(application, field, value)

  # Save changes to the database.
  db.commit()

  # Refresh the object with updated values.
  db.refresh(application)

  return application


def delete_application(
        db: Session,
        application: Application,
) -> None:
  # Delete the application from the database.
  db.delete(application)

  # Save the deletion.
  db.commit()
