import hashlib
import logging
import os
import pathlib
from os.path import join, splitext, basename
from typing import List
from zipfile import ZipFile, BadZipfile

from rarfile import RarFile, BadRarFile, NotRarFile

from app.enums.type_model import TypeModel
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel
from app.services.db_service import update_file, find_file_by_full_path, find_file_by_md5, insert_file, find_file
from app.tools import is_image

LOGGER = logging.getLogger(__name__)


def create_file_model(library_path: str, file_path: str):
    name, extension = splitext(basename(file_path))
    pages_list = count_pages(library_path, file_path)
    file_dict = {
        "full_path": file_path,
        "path": os.path.dirname(file_path),
        "name": name,
        "extension": extension,
        "type": TypeModel.FILE.value,
        "pages_count": len(pages_list),
        "pages_names": pages_list,
        "current_page": 0,
        "md5": calculate_md5(library_path, file_path)
    }
    return FileModel(**file_dict)


async def execute_action(library_name: str, file: FileModel, action: str) -> FileModel:
    """Execute the given reading action on the given reading file"""
    match action:
        case "+": return await next_page(library_name, file)
        case "-": return await prev_page(library_name, file)
        case _:   return await set_page(library_name, file, int(action))


def get_opener_lib(extension: str):
    """Find the library needed to open the file based on it's extension"""
    match extension.lower():
        case ".cbz":
            return ZipFile
        case ".cbr":
            return RarFile


def get_full_path(library_path: str, file_path: str) -> str:
    """Get the access path opf the file"""
    return join(library_path, file_path)


def calculate_md5(library_path: str, file_path: str) -> str:
    """Calculate md5 signature of a file"""
    return hashlib.md5(pathlib.Path(get_full_path(library_path, file_path)).read_bytes()).hexdigest()


async def get_file_from_db(library: LibraryModel, file_path: str) -> FileModel:
    """Get a file in the database or create it otherwise"""
    # Check if file exist in database with path
    LOGGER.debug(f"Searching for {file_path} existence in database")
    db_file = await find_file_by_full_path(library.name, file_path)
    if db_file:
        LOGGER.debug(f"{file_path} : database ok")
        return db_file
    else:
        # File is not found, calculate md5 and search it to make sure the file wasn't moved/renamed
        # Create a new FileModel to avoid recalculating md5 if it doesn't exist in database anyway
        try:
            file = create_file_model(library.path, file_path)
            LOGGER.debug(f"Searching for {file.name} md5 {file.md5} existence in database")
            db_file = await find_file_by_md5(library.name, file.md5)
            if not db_file:
                # If file isn't found by md5, add a new entry in the database
                insert_result = await insert_file(library.name, file)
                LOGGER.info(f"{file.full_path} : added new entry in database {insert_result.inserted_id}")
                return await find_file(library.name, insert_result.inserted_id)
            else:
                # Else update existing entry
                # WARNING: this will prevent duplicate file from being listed multiple times,
                # database will only mention last file found by md5
                LOGGER.info(f"{db_file.full_path} : updating to new location {file.full_path}")
                file_updated = UpdateFileModel.update_path(file_path)
                return await update_file(library.name, str(db_file.id), file_updated)

        except (BadZipfile, BadRarFile, NotRarFile):
            logging.error(f"Unreadable file : '{file_path}', ignoring file")


# Pages methods
def count_pages(library_path: str, file_path: str) -> List[str]:
    """Create a list of all the pages names in their naming order and count the result"""
    LOGGER.debug(f"{file_path} : Counting pages")
    opener_lib = get_opener_lib(splitext(basename(file_path))[1])
    pages_names = []
    with opener_lib(get_full_path(library_path, file_path), 'r') as file:
        for item in file.infolist():
            if is_image(item.filename):
                pages_names.append(item.filename)
        LOGGER.debug(f"{file_path} : {len(pages_names)} pages")
        return pages_names


def get_page(library_path: str, file_data: FileModel, num: int = 0):
    """Get a specific page with a given number"""
    opener_lib = get_opener_lib(file_data.extension)
    with opener_lib(get_full_path(library_path, file_data.full_path), 'r') as file:
        with file.open(file_data.pages_names[num]) as img:
            return img.read()


def get_current_page(library_path: str, file: FileModel):
    """Return file data corresponding to the current page number"""
    return get_page(library_path, file, file.current_page)


async def set_page(library_name: str, file: FileModel, num: int) -> FileModel:
    """Set the current page of a file in the database and return the updated FileModel object"""
    if 0 <= num <= file.pages_count - 1:
        return await update_file(library_name, str(file.id), UpdateFileModel(**{"current_page": num}))
    return file


async def next_page(library_name: str, file: FileModel) -> FileModel:
    """Increment current page for file"""
    return await set_page(library_name, file, file.current_page + 1)


async def prev_page(library_name: str, file: FileModel) -> FileModel:
    """Decrement current page for file"""
    return await set_page(library_name, file, file.current_page - 1)

