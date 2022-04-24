from os import listdir
from os.path import isfile, join

from fastapi import APIRouter

from app.endpoint import base_dir
from app.model.directory_model import DirectoryModel
from app.model.file_model import FileModel

router = APIRouter(prefix="/dir", tags=["Directory"], responses={404: {"directory": "Not found"}})


def get_dir_content(path: str):
    dirs = []
    files = []
    for item in listdir(base_dir + path):
        if isfile(join(base_dir, path, item)):
            files.append(FileModel(path=join(path, item)))
        else:
            dirs.append(DirectoryModel(name=item, path=join(path, item)))
    return dirs, files


@router.get("/")
async def get_root_content():
    return get_dir_content("")


@router.get("/{path}")
async def get_path_content(path: str):
    return get_dir_content(path)
