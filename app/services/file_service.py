import logging
import pathlib
import sys
from os.path import join, isfile

from fastapi.encoders import jsonable_encoder

from app.endpoint import base_dir
# from app.model.pdf_model import Pdf
from app.model.base_models.file_model import FileModel
from app.model.file import File
from app.services import Collections
from app.services.db_service import search_with_attributes, insert_one

LOGGER = logging.getLogger(__name__)


def find_file(path: str):
    """Find the file on the storage and depending on the format, return the proper object"""
    file_path = join(base_dir, path)
    if isfile(file_path):
        match pathlib.Path(path).suffix.lower():
            case ".cbz": return File(path=path)
            case ".cbr": return File(path=path)
            # case ".pdf": return Pdf(path=path)
            case _: return None
    return None


def execute_action(file: File, action: str):
    """Execute the given reading action on the given reading file"""
    match action:
        case "+": file.next_page()
        case "-": file.prev_page()
        case _: file.set_page(int(action))


async def check_db_sync(file: File):
    # Check if file exist in database with path
    search_dict = {"path": file.path}
    db_file = await search_with_attributes(search_dict, Collections.COMICS)
    if not db_file:
        # File is not found, calculate md5 and search it to make sure the file wasn't moved/renamed
        search_dict = {"md5": file.calculate_md5()}
        db_file = await search_with_attributes(search_dict, Collections.COMICS)
        if not db_file:
            # If file isn't found by md5, add a new entry in the database
            LOGGER.debug(f"{file.path} : not found in database, creating new")
            db_file = FileModel.from_orm(file)
            test = await insert_one(Collections.COMICS, jsonable_encoder(db_file.dict()))
            LOGGER.info(f"{file.path} : added new entry in database {test.inserted_id}")
        else:
            # Sinon mettre à jour l'entrée existante
            LOGGER.info(f"{file.path} : updating to new location {db_file['path']}")
    else:
        LOGGER.debug(f"{file.path} : scan ok")
