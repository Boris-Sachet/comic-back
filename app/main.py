import logging.config
from os import path

from fastapi import FastAPI

# log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
# logging.config.fileConfig(log_file_path)

from app.endpoint import directory_route, file_route, library_route

LOGGER = logging.getLogger(__name__)

app = FastAPI()

app.include_router(directory_route.router)
app.include_router(file_route.router)
app.include_router(library_route.router)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER.info("app is running")
