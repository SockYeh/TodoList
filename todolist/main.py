from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from todolist.backend.utils.config import env
from todolist.backend.utils.database import close_db, open_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:  # noqa: ARG001
    """Context manager for application lifespan."""
    await open_db()

    yield

    await close_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=env.AUTH_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = []
for router in routers:
    app.include_router(router)
