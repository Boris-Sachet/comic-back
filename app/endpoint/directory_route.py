from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.model.base_models.file_model import FileModel
from app.services.directory_service import get_dir_content, scan_in_depth

router = APIRouter(prefix="/dir", tags=["Directory"], responses={404: {"directory": "Not found"}})


@router.get("/", response_class=JSONResponse)
async def get_path_content(path: str = ""):
    dirs, files = get_dir_content(path)
    files_model = [FileModel.from_orm(file) for file in files]
    return dirs, files_model


@router.get("/scan")
async def scan_base_directory():
    await scan_in_depth("/")
