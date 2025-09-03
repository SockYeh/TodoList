from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["frontend"])
templates = Jinja2Templates(directory=r"./todolist/frontend")


@router.get("/")
async def root(request: Request) -> HTMLResponse:
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login")
async def login(request: Request) -> HTMLResponse:
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request) -> HTMLResponse:
    """Render the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/tasks")
async def tasks(request: Request) -> HTMLResponse:
    """Render the tasks page."""
    if not request.cookies.get("session"):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Please log in to access tasks."},
        )
    return templates.TemplateResponse("tasks.html", {"request": request})


@router.get("/logout")
async def logout(request: Request) -> HTMLResponse:
    """Render the logout page."""
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})
