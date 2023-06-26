import logging

from fastapi import FastAPI

from app import loging_config  # noqa: F401
from app.endpoint import file_route, library_route, root_route

LOGGER = logging.getLogger(__name__)

app = FastAPI()

app.include_router(root_route.router)
app.include_router(file_route.router)
app.include_router(library_route.router)

LOGGER.info("app is running")