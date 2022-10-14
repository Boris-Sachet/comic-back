from fastapi import APIRouter

from app.endpoint.base_models.custom_response_models import DirContentResponseModel
from app.services.directory_service import get_dir_content, scan_in_depth

router = APIRouter(prefix="/dir", tags=["Directory"], responses={404: {"directory": "Not found"}})


@router.get("/", response_model=DirContentResponseModel)
async def get_path_content(path: str = ""):
    return await get_dir_content(path)


@router.get("/scan")
async def scan_base_directory():
    await scan_in_depth("/")
