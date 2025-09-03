from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["frontend"])
templates = Jinja2Templates(directory=r"todolist\frontend")


@router.get("/login")
async def root(request: Request) -> HTMLResponse:
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request) -> HTMLResponse:
    """Render the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})
