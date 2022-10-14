import logging
import pathlib
from os import listdir
from os.path import isfile, join
from app.endpoint import base_dir
from app.model.base_models.directory_model import DirectoryModel
from app.services.file_service import get_file_from_db

LOGGER = logging.getLogger(__name__)


async def get_dir_content(path: str):
    """Return the content of the directory in two list, the list of subdirs and the list of supported files
     (as base model extensions)"""
    dirs = []
    files = []
    supported_extentions = [".cbz", ".cbr"]
    for item in listdir(base_dir + path):
        if isfile(join(base_dir, path, item)):
            if pathlib.Path(item).suffix in supported_extentions:
                if (db_file := await get_file_from_db(join(path, item))) is not None:
                    files.append(db_file)
        else:
            dirs.append(DirectoryModel.create(join(path, item)))
    return dirs, files


async def scan_in_depth(path: str):
    """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
    in database or add them if they're not"""
    # Scan base dir
    dirs, files = await get_dir_content(path)

    # Scan sub-folders
    for directory in dirs:
        await scan_in_depth(directory.path)
