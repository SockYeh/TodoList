import re

from fastapi import APIRouter, HTTPException, Request, status

from todolist.backend.schemas.auth import UserLogin, UserRegister
from todolist.backend.utils.database import DBErrors, authenticate_user, create_user

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, payload: UserRegister) -> None:  # noqa: ARG001
    """Register a new user."""
    email = payload.email
    username = payload.username
    password = payload.password

    if not re.match(r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    try:
        await create_user(email, username, password)
    except DBErrors.UserExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from e


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, payload: UserLogin) -> None:
    """Login a user."""
    email = payload.email
    password = payload.password

    try:
        user = await authenticate_user(email, password)
    except (DBErrors.PasswordMismatch, DBErrors.UserNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from e

    request.session["userid"] = str(user.id)
