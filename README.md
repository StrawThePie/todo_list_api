# Todo List API

A RESTful Todo List API built with FastAPI and SQLite.  
It implements user registration, login with JWT-style tokens, and CRUD operations on todos with authentication, pagination, filtering, and sorting, plus basic rate limiting and tests.  

Created for https://roadmap.sh/projects/todo-list-api

---

## Tech stack

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy
- Passlib (password hashing with pbkdf2_sha256)
- Python-JOSE (JWT tokens)
- SQLite (for persistence)
- Pytest (for tests)

---

## Running the app

1. **Create and activate virtualenv** (already done for this project):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt
```
(or install the individual packages you see in this project: ```fastapi```, ```uvicorn[standard]```, ```sqlalchemy```, ```pydantic```, ```passlib```, ```python-jose```, ```pytest```.)

3. **Create the database:**

```database.py``` defines the ```User``` and ```Todo``` models and calls ```Base.metadata.create_all(bind=engine)``` so tables are created on first run.

4. **Start the Server:**

```bash
uvicorn main:app --reload
```

5. **Open docs:**

Go to http://127.0.0.1:8000/docs to use the interactive Swagger UI.

___

## Endpoints

**Auth**

- ```POST /register```
    - Body: ```{ "name": "John Doe", "email": "john@doe.com", "password": "password" }```
      - Creates a user, hashes password, returns ```{ "token": "<access_token>" }```.

- ```POST /login```
    - Body: ```{ "email": "john@doe.com", "password": "password" }```
    - Validates credentials, returns a token payload (access token, and optionally refresh token).

**Todos (require ```Authorization: Bearer <token>``` header)**

- ```POST /todos```
    - Body: ```{ "title": "Buy groceries", "description": "Buy milk, eggs, and bread" }```
    - Returns created todo: ```{ "id": 1, "title": "...", "description": "..." }```.

- ```GET /todos```
  - Query: ```page```, ```limit```, ```optional search```, ```sort_by```, ```order```.
  - Returns:

```json
{
  "data": [ { "id": 1, "title": "...", "description": "..." } ],
  "page": 1,
  "limit": 10,
  "total": 1
}
```

- ```PUT /todos/{id}```
    - Only the owner can update; otherwise returns 403 with ```{ "message": "Forbidden" }```.

  - ```DELETE /todos/{id}```
  - Only the owner can delete; on success returns status ```204```.

___


**Validation, auth, and security**

- Pydantic schemas enforce:
    - Non-empty names and titles, max lengths.
    - Valid email addresses. 
    - Minimum password length.


- Passwords are hashed using ```pbkdf2_sha256``` via Passlib.

- Tokens are JWTs signed with ```HS256``` and contain user id in the ```sub``` claim.

- A dependency (```get_current_user```) reads the ```Authorization``` header, validates the token, and loads the current user for protected routes.

- Basic rate limiting middleware restricts requests per IP and endpoint.

___


**Testing**

Tests live under ```tests/``` and use a separate SQLite database.

Run all tests:

```bash
pytest
```

Covered scenarios include:

- Register and login success.
- Duplicate email and invalid login errors.
- Todo creation/listing with auth.
- Authorization checks (user cannot edit/delete others' todos).
- Pagination behavior in GET /todos.

___