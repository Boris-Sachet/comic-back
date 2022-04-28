import pathlib
from os.path import isfile, join

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.endpoint import base_dir
from app.model.cbz_model import Cbz
from app.model.file import File

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
        match pathlib.Path(path).suffix:
            case ".cbz": file = Cbz(path=file_path)
            case _: raise HTTPException(status_code=415, detail="Unreadable file format")
        return StreamingResponse(file.iterfile())
