from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Hash the plain password using Argon2.
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    # Verify the plain password against the stored hash.
    return password_hash.verify(plain_password, hashed_password)