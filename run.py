if __name__ == "__main__":
    import uvicorn

    uvicorn.run("todolist.main:app", host="0.0.0.0", port=8000)  # noqa: S104
