import pytest


def test_create_application(authenticated_client, sample_job):
  response = authenticated_client.post(
    "/api/v1/applications/",
    json={
      "job_id": sample_job.id,
      "notes": "Interested in this position",
    },
  )

  assert response.status_code == 201

  data = response.json()

  assert data["job_id"] == sample_job.id
  assert data["status"] == "applied"
  assert data["notes"] == "Interested in this position"
  assert "id" in data
  assert "user_id" in data


def test_create_duplicate_application(authenticated_client, sample_job):
  # Create the first application.
  authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  # Try to create the same application again.
  response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  assert response.status_code == 409
  assert response.json()["detail"] == (
    "Application already exists or job does not exist"
  )


def test_get_applications(authenticated_client, sample_job):
  # Create an application.
  authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  # Get the user's applications.
  response = authenticated_client.get("/api/v1/applications/")

  assert response.status_code == 200

  data = response.json()

  assert len(data) == 1
  assert data[0]["job_id"] == sample_job.id
  assert data[0]["status"] == "applied"


def test_get_applications_only_for_current_user(
        authenticated_client,
        second_user_auth_headers,
        sample_job,
):
  # Create an application as the first user.
  authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  # Get applications as the second user.
  response = authenticated_client.get(
    "/api/v1/applications/",
    headers=second_user_auth_headers,
  )

  assert response.status_code == 200
  assert response.json() == []


def test_get_application_by_id(authenticated_client, sample_job):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Get the application by its ID.
  response = authenticated_client.get(
    f"/api/v1/applications/{application_id}"
  )

  assert response.status_code == 200
  assert response.json()["id"] == application_id
  assert response.json()["job_id"] == sample_job.id


def test_user_cannot_get_another_users_application(
        authenticated_client,
        second_user_auth_headers,
        sample_job,
):
  # Create an application as the first user.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Try to get the application as the second user.
  response = authenticated_client.get(
    f"/api/v1/applications/{application_id}",
    headers=second_user_auth_headers,
  )

  assert response.status_code == 404
  assert response.json()["detail"] == "Application not found"


def test_update_application(authenticated_client, sample_job):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Update the application.
  response = authenticated_client.put(
    f"/api/v1/applications/{application_id}",
    json={
      "status": "interview",
      "notes": "Interview scheduled",
    },
  )

  assert response.status_code == 200

  data = response.json()

  assert data["id"] == application_id
  assert data["status"] == "interview"
  assert data["notes"] == "Interview scheduled"


def test_user_cannot_update_another_users_application(
        authenticated_client,
        second_user_auth_headers,
        sample_job,
):
  # Create an application as the first user.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Try to update the application as the second user.
  response = authenticated_client.put(
    f"/api/v1/applications/{application_id}",
    headers=second_user_auth_headers,
    json={
      "status": "interview",
      "notes": "Trying to update another user's application",
    },
  )

  assert response.status_code == 404
  assert response.json()["detail"] == "Application not found"


def test_delete_application(authenticated_client, sample_job):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Delete the application.
  response = authenticated_client.delete(
    f"/api/v1/applications/{application_id}"
  )

  assert response.status_code == 204

  # Verify that the application no longer exists.
  get_response = authenticated_client.get(
    f"/api/v1/applications/{application_id}"
  )

  assert get_response.status_code == 404


def test_user_cannot_delete_another_users_application(
        authenticated_client,
        second_user_auth_headers,
        sample_job,
):
  # Create an application as the first user.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Try to delete the application as the second user.
  response = authenticated_client.delete(
    f"/api/v1/applications/{application_id}",
    headers=second_user_auth_headers,
  )

  assert response.status_code == 404
  assert response.json()["detail"] == "Application not found"

  # Verify that the application still exists for the first user.
  owner_response = authenticated_client.get(
    f"/api/v1/applications/{application_id}"
  )

  assert owner_response.status_code == 200


def test_update_application_with_invalid_status(
        authenticated_client,
        sample_job,
):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Try to update the application with an invalid status.
  response = authenticated_client.put(
    f"/api/v1/applications/{application_id}",
    json={"status": "banana"},
  )

  assert response.status_code == 422


@pytest.mark.parametrize(
  "valid_status",
  ["applied", "interview", "rejected", "accepted"],
)
def test_update_application_with_valid_status(
        authenticated_client,
        sample_job,
        valid_status,
):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Update the application with a valid status.
  response = authenticated_client.put(
    f"/api/v1/applications/{application_id}",
    json={"status": valid_status},
  )

  assert response.status_code == 200
  assert response.json()["status"] == valid_status


def test_update_application_with_null_status(
        authenticated_client,
        sample_job,
):
  # Create an application.
  create_response = authenticated_client.post(
    "/api/v1/applications/",
    json={"job_id": sample_job.id},
  )

  application_id = create_response.json()["id"]

  # Try to update the application with a null status.
  response = authenticated_client.put(
    f"/api/v1/applications/{application_id}",
    json={"status": None},
  )

  assert response.status_code == 422
