from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["frontend"])
templates = Jinja2Templates(directory=r"todolist\frontend")
