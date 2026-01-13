def test_register_returns_token(client):
    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert "token" in body


def test_register_duplicate_email_400(client):
    client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "dup@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/register",
        json={
            "name": "Another",
            "email": "dup@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert "detail" in body


def test_login_success_returns_token(client):
    email = "login@example.com"
    password = "password123"

    client.post(
        "/register",
        json={
            "name": "Login User",
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    body = response.json()
    assert "token" in body or "access_token" in body


def test_login_invalid_credentials_401(client):
    response = client.post(
        "/login",
        json={"email": "nope@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
