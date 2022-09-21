from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.directory_service import get_dir_content

router = APIRouter(prefix="/dir", tags=["Directory"], responses={404: {"directory": "Not found"}})


@router.get("/", response_class=JSONResponse)
async def get_root_content():
    return get_dir_content("")


@router.get("/{path}", response_class=JSONResponse)
async def get_path_content(path: str):
    return get_dir_content(path)
