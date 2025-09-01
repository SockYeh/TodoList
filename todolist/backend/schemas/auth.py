from pydantic import BaseModel


class UserRegister(BaseModel):
    """Schema for user registration."""

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str
    password: str
