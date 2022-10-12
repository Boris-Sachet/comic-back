import logging
import pathlib
from os import listdir
from os.path import isfile, join
from zipfile import BadZipfile

from rarfile import BadRarFile, NotRarFile

from app.endpoint import base_dir
from app.model.directory import Directory
from app.model.file import File
from app.services.file_service import check_db_sync

LOGGER = logging.getLogger(__name__)

def get_dir_content(path: str):
    """Return the content of the directory in two list, the list of subdirs and the list of supported files
     (as base model extensions)"""
    dirs = []
    files = []
    supported_extentions = [".cbz", ".cbr"]
    for item in listdir(base_dir + path):
        if isfile(join(base_dir, path, item)):
            if pathlib.Path(item).suffix in supported_extentions:
                try:
                    files.append(File(path=join(path, item)))
                    # match pathlib.Path(item).suffix:  # Match to ignore unsupported files types
                    #     case ".cbz": files.append(FileModel.from_orm(File(path=join(path, item))))
                    #     case ".cbr": files.append(FileModel.from_orm(File(path=join(path, item))))
                    #     # case _: files.append(FileModel.from_orm(File(path=join(path, item))))
                except (BadZipfile, BadRarFile, NotRarFile):
                    logging.error(f"Unreadable file : '{join(path, item)}', ignoring file")
        else:
            dirs.append(Directory(path=join(path, item)))
    return dirs, files


async def scan_in_depth(path: str):
    """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
    in database or add them if they're not"""
    # Scan base dir
    dirs, files = get_dir_content(path)
    for file in files:
        await check_db_sync(file)

    # Scan sub-folders
    for directory in dirs:
        await scan_in_depth(directory.path)
