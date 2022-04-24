from os.path import isfile, join
from zipfile import ZipFile

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse

from app.endpoint import base_dir
from app.model.cbz_model import CbzModel

router = APIRouter(prefix="/file", tags=["File"], responses={404: {"file": "Not found"}})


@router.get("/{path}", response_class=FileResponse)
async def get_file(path: str):
    file_path = join(base_dir, path)
    if isfile(file_path):
        return FileResponse(file_path)

@router.get("/stream/{path}")
async def stream_file(path: str):
    file_path = join(base_dir, path)
    if isfile(file_path):
        file = CbzModel(path=file_path, name="osef")
        return StreamingResponse(file.iterfile())
