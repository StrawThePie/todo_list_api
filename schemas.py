from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
