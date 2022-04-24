from fastapi import FastAPI

from app.endpoint import directory_route, file_route

app = FastAPI()

app.include_router(directory_route.router)
app.include_router(file_route.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
