from fastapi import APIRouter

from app.endpoint.base_models.custom_response_models import LibContentResponseModel
from app.services.db_service import db_find_library_by_name
from app.services.directory_service import get_dir_content, scan_in_depth

router = APIRouter(prefix="/dir", tags=["Directory"], responses={404: {"directory": "Not found"}})


# TODO Move this to library route
@router.get("/", response_model=LibContentResponseModel)
async def get_path_content(library_name: str, path: str = ""):
    library = await db_find_library_by_name(library_name)
    return await get_dir_content(library, path)


# TODO Move this to library route
@router.get("/scan")
async def scan_base_directory(library_name: str):
    library = await db_find_library_by_name(library_name)
    await scan_in_depth(library, "/")
