def _create_user_and_token(client, email: str):
    password = "password123"

    client.post(
        "/register",
        json={
            "name": "Todo User",
            "email": email,
            "password": password,
        },
    )
    resp = client.post(
        "/login",
        json={"email": email, "password": password},
    )
    data = resp.json()
    token = data.get("token") or data.get("access_token")
    return token


def test_create_todo_requires_auth_401(client):
    response = client.post(
        "/todos",
        json={"title": "Test", "description": "No auth"},
    )
    assert response.status_code == 401


def test_create_and_list_todos(client):
    token = _create_user_and_token(client, "todo_user1@example.com")

    create_resp = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Buy milk", "description": "2%"},
    )
    assert create_resp.status_code == 201
    todo = create_resp.json()
    assert todo["title"] == "Buy milk"

    list_resp = client.get(
        "/todos?page=1&limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] >= 1
    assert len(body["data"]) >= 1


def test_update_forbidden_for_other_user(client):
    owner_token = _create_user_and_token(client, "owner@example.com")
    create_resp = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"title": "Secret", "description": "Owner only"},
    )
    todo_id = create_resp.json()["id"]

    other_token = _create_user_and_token(client, "other@example.com")

    update_resp = client.put(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "Hacked", "description": "Changed"},
    )
    assert update_resp.status_code == 403


def test_delete_todo_204(client):
    token = _create_user_and_token(client, "deleter@example.com")
    create_resp = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Temp", "description": "To delete"},
    )
    todo_id = create_resp.json()["id"]

    delete_resp = client.delete(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    list_resp = client.get(
        "/todos?page=1&limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    ids = [t["id"] for t in list_resp.json()["data"]]
    assert todo_id not in ids
