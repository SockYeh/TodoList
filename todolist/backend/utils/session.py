from fastapi import HTTPException, Request


async def validate_session(request: Request) -> None:
    """Validate the session of the user."""
    try:
        request.session["user_id"]
    except KeyError as e:
        raise HTTPException(status_code=401, detail="Invalid Session!") from e
