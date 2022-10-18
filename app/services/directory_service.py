import logging
import pathlib
from os import listdir
from os.path import isfile, join
from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.file_service import get_file_from_db, get_full_path

LOGGER = logging.getLogger(__name__)


async def get_dir_content(library: LibraryModel, path: str):
    """Return the content of the directory in two list, the list of subdirs and the list of supported files
     (as base model extensions)"""
    dirs = []
    files = []
    supported_extentions = [".cbz", ".cbr"]
    for item in listdir(library.path + path):
        if isfile(get_full_path(library.path, join(path, item))):
            if pathlib.Path(item).suffix in supported_extentions:
                if (db_file := await get_file_from_db(library, join(path, item))) is not None:
                    files.append(db_file)
        else:
            dirs.append(DirectoryModel.create(join(path, item)))
    return dirs, files


async def scan_in_depth(library: LibraryModel, path: str):
    """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
    in database or add them if they're not"""
    # Scan base dir
    dirs, files = await get_dir_content(library, path)

    # Scan sub-folders
    for directory in dirs:
        await scan_in_depth(library, directory.path)
