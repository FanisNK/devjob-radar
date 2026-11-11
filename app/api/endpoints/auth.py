from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.user_service import create_user, get_user_by_email



router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    # Check whether a user with this email already exists.
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    try:
        # Create a new user with a hashed password.
        return create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
        )
    except IntegrityError:
        # Handle a duplicate email in case of a concurrent request.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Find the user by email.
    user = get_user_by_email(db, form_data.username)

    # Check the password and return an error if credentials are invalid.
    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check whether the user account is active.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    # Create an access token containing the user's ID.
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    # Return the access token.
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }