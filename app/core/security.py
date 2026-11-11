from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def hash_password(password: str) -> str:
    # Hash the plain password using Argon2.
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    # Verify the plain password against the stored hash.
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    # Copy the payload to avoid modifying the original dictionary.
    to_encode = data.copy()

    # Set the token expiration time.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add the expiration time to the token payload.
    to_encode.update({"exp": expire})

    # Create and sign the JWT token.
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    # Decode the JWT token and verify its signature.
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"],
    )

    return payload


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # Define the authentication error.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate the JWT token.
        payload = decode_access_token(token)

        # Get the user ID from the token payload.
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Convert the user ID to an integer.
        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    # Find the user in the database.
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user