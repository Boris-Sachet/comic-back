import logging
import pathlib
import smbclient
from os import listdir
from os.path import isfile, join, normpath
from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.file_service import get_file_from_db, get_full_path

LOGGER = logging.getLogger(__name__)


async def get_dir_content(library: LibraryModel, path: str):
    """Return the content of the directory in two list, the list of subdirs and the list of supported files
     (as base model extensions)"""
    supported_extentions = [".cbz", ".cbr"]
    if library.connect_type == "local":
        return await get_local_dir_content(library, path, supported_extentions)
    if library.connect_type == "smb":
        return await get_smb_dir_content(library, path, supported_extentions)


async def get_local_dir_content(library: LibraryModel, path: str, supported_extentions: list):
    """Return the content of the local directory in two list, the list of subdirs and the list of supported files
         (as base model extensions)"""
    dirs = []
    files = []
    for item in listdir(library.path + path):
        if isfile(get_full_path(library, join(path, item))):
            if pathlib.Path(item).suffix in supported_extentions:
                if (db_file := await get_file_from_db(library, join(path, item))) is not None:
                    files.append(db_file)
        else:
            dirs.append(DirectoryModel.create(join(path, item)))
    return dirs, files


async def get_smb_dir_content(library: LibraryModel, path: str, supported_extentions: list):
    """Return the content of the local directory in two list, the list of subdirs and the list of supported files
         (as base model extensions)"""
    dirs = []
    files = []
    smb_info = {"username": library.user, "password": library.password}
    for item in smbclient.scandir(path=get_full_path(library, path), **smb_info):
        if item.is_file():
            if pathlib.Path(item.name).suffix in supported_extentions:
                if (db_file := await get_file_from_db(library, path + '\\' + item.name)) is not None:
                    files.append(db_file)
            else:
                dirs.append(DirectoryModel.create(join(path, item.name)))
    return dirs, files


async def scan_in_depth(library: LibraryModel, path: str):
    """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
    in database or add them if they're not"""
    # Scan base dir
    dirs, files = await get_dir_content(library, path)

    # Scan sub-folders
    for directory in dirs:
        await scan_in_depth(library, directory.path)
