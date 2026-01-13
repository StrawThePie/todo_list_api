from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import User, Todo
from deps import get_db
from schemas import (
    UserCreate,
    Token,
    LoginRequest,
    TodoCreate,
    TodoUpdate,
    TodoOut,
    TodoListOut,
)
from auth import (
    hash_password,
    create_access_token,
    verify_password,
    get_current_user,
)


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Todo List API"}


@app.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"token": token}


@app.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id)})
    return {"token": token}


@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = Todo(
        title=todo_in.title,
        description=todo_in.description,
        user_id=current_user.id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.get("/todos", response_model=TodoListOut)
def list_todos(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort_by: str = "id",        # or "title" / "created_at"
    order: str = "asc",         # "asc" or "desc"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    query = db.query(Todo).filter(Todo.user_id == current_user.id)

    if search:
        query = query.filter(Todo.title.ilike(f"%{search}%"))

    if sort_by == "title":
        sort_column = Todo.title
    else:
        sort_column = Todo.id  # use Todo.created_at if you added it

    if order == "desc":
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)

    total = query.count()
    items = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return TodoListOut(data=items, page=page, limit=limit, total=total)


@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    todo.title = todo_in.title
    todo.description = todo_in.description
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    db.delete(todo)
    db.commit()
    return
