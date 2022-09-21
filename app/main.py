from fastapi import FastAPI

from app.endpoint import directory_route, file_route

app = FastAPI()

app.include_router(directory_route.router)
app.include_router(file_route.router)
