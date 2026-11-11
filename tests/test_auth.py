# Test that a user can register successfully.
def test_register_user(client):
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePassword123",
    }

    # Send a POST request to register a new user.
    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    # Check that the API returns 201 Created.
    assert response.status_code == 201

    # Check that the response contains the user's email.
    assert response.json()["email"] == user_data["email"]

    # Check that the response does not expose the hashed password.
    assert "hashed_password" not in response.json()



# Test that the API rejects registration with an existing email.
def test_register_user_with_existing_email(client):
    user_data = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123",
    }

    # Register the user for the first time.
    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    # Check that the first registration is successful.
    assert first_response.status_code == 201

    # Try to register the same email again.
    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    # Check that the API returns 409 Conflict.
    assert second_response.status_code == 409

    # Check the error message.
    assert second_response.json()["detail"] == "A user with this email already exists"



# Test that a user can log in successfully.
def test_login_user(client):
    user_data = {
        "email": "login@example.com",
        "password": "SecurePassword123",
    }

    # Register a new user before testing login.
    client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    # Send login credentials as form data.
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    # Check that the API returns 200 OK.
    assert response.status_code == 200

    # Check that the response contains an access token.
    assert "access_token" in response.json()

    # Check that the token type is bearer.
    assert response.json()["token_type"] == "bearer"



# Test that the API rejects login with an incorrect password.
def test_login_with_wrong_password(client):
    user_data = {
        "email": "wrongpassword@example.com",
        "password": "CorrectPassword123",
    }

    # Register a new user.
    client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    # Try to log in with an incorrect password.
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": "WrongPassword123",
        },
    )

    # Check that the API returns 401 Unauthorized.
    assert response.status_code == 401

    # Check the error message.
    assert response.json()["detail"] == "Incorrect email or password"



# Test that users cannot access jobs without an access token.
def test_access_jobs_without_token(client):
    # Send a request without an authorization header.
    response = client.get("/api/v1/jobs/")

    # Check that the API returns 401 Unauthorized.
    assert response.status_code == 401

    # Check the error message.
    assert response.json()["detail"] == "Not authenticated"
