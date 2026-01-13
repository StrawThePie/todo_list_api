from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    password: constr(min_length=6, max_length=128)


class Token(BaseModel):
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TodoBase(BaseModel):
    title: constr(min_length=1, max_length=255)
    description: Optional[constr(max_length=2000)] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    pass


class TodoOut(TodoBase):
    id: int

    class Config:
        orm_mode = True


class TodoListOut(BaseModel):
    data: List[TodoOut]
    page: int
    limit: int
    total: int
