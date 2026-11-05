# Test that the API returns a list of jobs.
def test_read_jobs(client):
    response = client.get("/api/v1/jobs/")

    # Check that the request was successful.
    assert response.status_code == 200

    # Check that the response contains a list.
    assert isinstance(response.json(), list)


# Test that the API returns a specific job by its ID.
def test_read_job(client, sample_job):
    response = client.get(f"/api/v1/jobs/{sample_job.id}")

    # Check that the request was successful.
    assert response.status_code == 200

    # Convert the JSON response into a Python dictionary.
    job = response.json()

    # Check that the returned job has the expected ID.
    assert job["id"] == sample_job.id

    # Check that the job contains the expected title.
    assert job["title"] == "Test Python Developer"


# Test that the API returns 404 for a job that does not exist.
def test_read_nonexistent_job(client):
    response = client.get("/api/v1/jobs/999999")

    # Check that the API returns a 404 status code.
    assert response.status_code == 404

    # Check the error message.
    assert response.json()["detail"] == "Job not found"


# Test that the API creates a new job successfully.
def test_create_job(client):
    job_data = {
        "title": "Junior Python Backend Developer",
        "company": "Test API Company",
        "description": "A test job created by pytest",
        "salary_min": 1500,
        "salary_max": 2500,
        "url": "https://example.com/jobs/pytest-create-001",
    }

    # Send a POST request with the job data.
    response = client.post("/api/v1/jobs/", json=job_data)

    # Check that the API returns 201 Created.
    assert response.status_code == 201

    # Convert the JSON response into a Python dictionary.
    created_job = response.json()

    # Check that the returned job contains the expected data.
    assert created_job["title"] == job_data["title"]
    assert created_job["company"] == job_data["company"]
    assert created_job["salary_min"] == job_data["salary_min"]
    assert created_job["salary_max"] == job_data["salary_max"]
    assert created_job["url"] == job_data["url"]

    # Check that the database generated a job ID.
    assert created_job["id"] is not None


# Test that the API updates an existing job successfully.
def test_update_job(client, sample_job):
    update_data = {
        "title": "Updated Python Backend Developer",
        "company": "Updated Test Company",
        "description": "Updated job description",
        "salary_min": 2500,
        "salary_max": 4000,
        "url": "https://example.com/jobs/updated-python-developer",
    }

    # Send a PUT request with the updated job data.
    response = client.put(
        f"/api/v1/jobs/{sample_job.id}",
        json=update_data,
    )

    # Check that the API returns 200 OK.
    assert response.status_code == 200

    # Convert the JSON response into a Python dictionary.
    updated_job = response.json()

    # Check that the job contains the updated data.
    assert updated_job["title"] == update_data["title"]
    assert updated_job["company"] == update_data["company"]
    assert updated_job["salary_min"] == update_data["salary_min"]
    assert updated_job["salary_max"] == update_data["salary_max"]
    assert updated_job["url"] == update_data["url"]


# Test that the API deletes an existing job successfully.
def test_delete_job(client, sample_job):
    job_id = sample_job.id

    # Send a DELETE request for the test job.
    response = client.delete(f"/api/v1/jobs/{job_id}")

    # Check that the API returns 204 No Content.
    assert response.status_code == 204

    # Check that the deleted job is no longer available.
    response = client.get(f"/api/v1/jobs/{job_id}")

    # Check that the API returns 404 Not Found.
    assert response.status_code == 404


# Test that the API rejects a job with a duplicate URL.
def test_create_job_with_duplicate_url(client, sample_job):
    # Prepare job data using an existing job URL.
    job_data = {
        "title": "Another Python Developer",
        "company": "Another Company",
        "description": "Another test job description",
        "salary_min": 3000,
        "salary_max": 4000,
        "url": sample_job.url,
    }

    # Send a POST request with the duplicate URL.
    response = client.post("/api/v1/jobs/", json=job_data)

    # Check that the API returns 409 Conflict.
    assert response.status_code == 409

    # Check that the response contains the expected error message.
    assert response.json()["detail"] == "A job with this URL already exists"


# Test that the API rejects invalid salary values.
def test_create_job_with_invalid_salary(client):
    # Prepare job data where the minimum salary exceeds the maximum.
    job_data = {
        "title": "Python Backend Developer",
        "company": "Test Company",
        "description": "A test job description",
        "salary_min": 5000,
        "salary_max": 3000,
        "url": "https://example.com/jobs/invalid-salary-test",
    }

    # Send a POST request with invalid salary values.
    response = client.post("/api/v1/jobs/", json=job_data)

    # Check that the API returns 422 Unprocessable Entity.
    assert response.status_code == 422


# Test that the API returns 404 when updating a nonexistent job.
def test_update_nonexistent_job(client):
    # Prepare updated job data.
    job_data = {
        "title": "Python Backend Developer",
        "company": "Test Company",
        "description": "Updated test description",
        "salary_min": 3000,
        "salary_max": 5000,
        "url": "https://example.com/jobs/nonexistent-update",
    }

    # Send a PUT request for a nonexistent job.
    response = client.put("/api/v1/jobs/999999", json=job_data)

    # Check that the API returns 404 Not Found.
    assert response.status_code == 404


# Test that the API returns 404 when deleting a nonexistent job.
def test_delete_nonexistent_job(client):
    # Send a DELETE request for a nonexistent job.
    response = client.delete("/api/v1/jobs/999999")

    # Check that the API returns 404 Not Found.
    assert response.status_code == 404

    # Check the error message.
    assert response.json()["detail"] == "Job not found"