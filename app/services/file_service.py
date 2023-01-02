import hashlib
import io
import logging
import os
import pathlib
from os.path import join, splitext, basename, isfile
from typing import List
from zipfile import ZipFile, BadZipfile
from rarfile import RarFile, BadRarFile, NotRarFile
from PIL import Image

from app.enums.type_model import TypeModel
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel
from app.services.db_service import db_update_file, db_find_file_by_full_path, db_find_file_by_md5, db_insert_file, \
    db_find_file, db_find_all_files, db_delete_file
from app.tools import is_image

LOGGER = logging.getLogger(__name__)


class FileService:
    @staticmethod
    def create_file_model(library: LibraryModel, file_path: str):
        name, extension = splitext(basename(file_path))
        pages_list = FileService.count_pages(library, file_path)
        file_dict = {
            "full_path": file_path,
            "path": os.path.dirname(file_path),
            "name": name,
            "extension": extension,
            "type": TypeModel.FILE.value,
            "pages_count": len(pages_list),
            "pages_names": pages_list,
            "current_page": 0,
            "md5": FileService.calculate_md5(library, file_path)
        }
        return FileModel(**file_dict)

    @staticmethod
    async def execute_action(library: LibraryModel, file: FileModel, action: str) -> FileModel:
        """Execute the given reading action on the given reading file"""
        match action:
            case "+":
                return await FileService.next_page(library, file)
            case "-":
                return await FileService.prev_page(library, file)
            case _:
                return await FileService.set_page(library, file, int(action))

    @staticmethod
    def get_opener_lib(extension: str):
        """Find the library needed to open the file based on it's extension"""
        match extension.lower():
            case ".cbz":
                return ZipFile
            case ".cbr":
                return RarFile
            case _:
                raise ValueError(f"Invalid file extension: {extension}")

    @staticmethod
    def get_full_path(library: LibraryModel, file_path: str) -> str:
        """Get the access path of the file"""
        if library.connect_type == "local":
            return join(library.path, file_path)
        if library.connect_type == "smb":
            return library.path + "\\" + file_path

    @staticmethod
    def calculate_md5(library: LibraryModel, file_path: str) -> str:
        """Calculate md5 signature of a file"""
        return hashlib.md5(pathlib.Path(FileService.get_full_path(library, file_path)).read_bytes()).hexdigest()

    @staticmethod
    async def get_file_from_db(library: LibraryModel, file_path: str) -> FileModel:
        """Get a file in the database or create it otherwise"""
        # Check if file exist in database with path
        LOGGER.debug(f"Searching for {file_path} existence in database")
        db_file = await db_find_file_by_full_path(library.name, file_path)
        if db_file:
            LOGGER.debug(f"{file_path} : database ok")
            return db_file
        else:
            # File is not found, calculate md5 and search it to make sure the file wasn't moved/renamed
            # Create a new FileModel to avoid recalculating md5 if it doesn't exist in database anyway
            try:
                file = FileService.create_file_model(library, file_path)
                LOGGER.debug(f"Searching for {file.name} md5 {file.md5} existence in database")
                db_file = await db_find_file_by_md5(library.name, file.md5)
                if file.pages_count == 0:
                    LOGGER.error(f"File : '{file_path}', no readable pages found, ignoring file")
                else:
                    if not db_file:
                        # If file isn't found by md5, add a new entry in the database
                        insert_result = await db_insert_file(library.name, file)
                        LOGGER.info(f"{file.full_path} : added new entry in database {insert_result.inserted_id}")
                        return await db_find_file(library.name, insert_result.inserted_id)
                    else:
                        # TODO Before updating check if old file exist, if yes allow duplicate and create new entry in db
                        # Else update existing entry
                        # WARNING: this will prevent duplicate file from being listed multiple times,
                        # database will only mention last file found by md5
                        LOGGER.info(f"{db_file.full_path} : updating to new location {file.full_path}")
                        file_updated = UpdateFileModel.update_path(file_path)
                        return await db_update_file(library.name, str(db_file.id), file_updated)
            except (BadZipfile, BadRarFile, NotRarFile):
                LOGGER.error(f"Unreadable file : '{file_path}', ignoring file")

    @staticmethod
    async def purge_deleted_files(library: LibraryModel):
        """This method will look at every file reference in database and check if there is an actual file on the
        corresponding path, if no file is found the database entry is removed.
        WARNING: This method is designed to be run just after a scan and might remove wrong data if the database is not
        up-to-date"""
        LOGGER.debug("File purge started")
        files = await db_find_all_files(library.name)
        for file in files:
            if not isfile(FileService.get_full_path(library, file["full_path"])):
                await db_delete_file(library.name, str(file["id"]))
                LOGGER.info(f"File {file['name']} purged from library {library.name} because no actual file was found")
        LOGGER.debug("File purge ended")

    # Pages methods
    @staticmethod
    def count_pages(library: LibraryModel, file_path: str) -> List[str]:
        """Create a list of all the pages names in their naming order and count the result"""
        LOGGER.debug(f"{file_path} : Counting pages")
        opener_lib = FileService.get_opener_lib(splitext(basename(file_path))[1])
        pages_names = []
        with opener_lib(FileService.get_full_path(library, file_path), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    pages_names.append(item.filename)
            LOGGER.debug(f"{file_path} : {len(pages_names)} pages")
            return pages_names

    @staticmethod
    def get_page(library: LibraryModel, file_data: FileModel, num: int = 0) -> bytes:
        """Get a specific page with a given number"""
        opener_lib = FileService.get_opener_lib(file_data.extension)
        with opener_lib(FileService.get_full_path(library, file_data.full_path), 'r') as file:
            try:
                with file.open(file_data.pages_names[num]) as img:
                    return img.read()
            except Exception as e:
                print(file_data)  # TODO manage the error when files have 0 pages

    @staticmethod
    def get_current_page(library: LibraryModel, file: FileModel):
        """Return file data corresponding to the current page number"""
        return FileService.get_page(library, file, file.current_page)

    @staticmethod
    async def set_page(library: LibraryModel, file: FileModel, num: int) -> FileModel:
        """Set the current page of a file in the database and return the updated FileModel object"""
        if 0 <= num <= file.pages_count - 1:
            return await db_update_file(library.name, str(file.id), UpdateFileModel(**{"current_page": num}))
        return file

    @staticmethod
    async def next_page(library: LibraryModel, file: FileModel) -> FileModel:
        """Increment current page for file"""
        return await FileService.set_page(library, file, file.current_page + 1)

    @staticmethod
    async def prev_page(library: LibraryModel, file: FileModel) -> FileModel:
        """Decrement current page for file"""
        return await FileService.set_page(library, file, file.current_page - 1)

    @staticmethod
    def generate_thumbnail_cover(library: LibraryModel, file: FileModel) -> Image:
        """Generate a thumbnail cover for the given file"""
        cover_bytes = FileService.get_page(library, file, 0)
        cover = Image.open(io.BytesIO(cover_bytes))
        cover.thumbnail((400, 400))
        return cover
