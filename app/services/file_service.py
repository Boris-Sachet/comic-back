from datetime import datetime
import io
import logging
import os
from os.path import join, splitext, basename, isfile
from zipfile import ZipFile, BadZipfile
from rarfile import RarFile, BadRarFile, NotRarFile
from PIL import Image
from smb.SMBConnection import SMBConnection

from app.enums.type_model import TypeModel
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel
from app.services.db_service import db_update_file, db_find_file_by_full_path, db_find_file_by_md5, db_insert_file, \
    db_find_file, db_find_all_files, db_delete_file
from app.services.storage_service import StorageService

LOGGER = logging.getLogger(__name__)


class FileService:
    @staticmethod
    def create_file_model(library: LibraryModel, file_path: str, storage: StorageService = None):
        name, extension = splitext(basename(file_path))
        if not storage:
            storage = StorageService(library)
        pages_list = storage.list_pages(file_path, FileService.get_opener_lib(splitext(basename(file_path))[1]))
        file_dict = {
            "full_path": file_path,
            "path": os.path.dirname(file_path),
            "name": name,
            "extension": extension,
            "type": TypeModel.FILE.value,
            "pages_count": len(pages_list),
            "pages_names": pages_list,
            "current_page": 0,
            "md5": storage.calculate_md5(file_path)
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
    async def get_file_from_db(library: LibraryModel, file_path: str, storage: StorageService = None) -> FileModel:
        """Get a file in the database or create it otherwise"""
        if not storage:
            storage = StorageService(library)
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
                file = FileService.create_file_model(library, file_path, storage)
                LOGGER.debug(f"Searching for {file.name} md5 {file.md5} existence in database")
                db_file = await db_find_file_by_md5(library.name, file.md5)
                if file.pages_count == 0:
                    LOGGER.error(f"File : '{file_path}', no readable pages found, ignoring file")
                else:
                    if not db_file:
                        # If file isn't found by md5, add a new entry in the database
                        file.add_date = datetime.now()
                        file.update_date = file.add_date
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
    async def purge_deleted_files(library: LibraryModel, storage: StorageService = None):
        """This method will look at every file reference in database and check if there is an actual file on the
        corresponding path, if no file is found the database entry is removed.
        WARNING: This method is designed to be run just after a scan and might remove wrong data if the database is not
        up-to-date"""
        LOGGER.info("File purge started")
        files = await db_find_all_files(library.name)
        if not storage:
            storage = StorageService(library)
        for file in files:
            if not storage.isfile(file["full_path"]):
                await db_delete_file(library.name, str(file["_id"]))
                storage.delete_thumbnail(FileModel(**file))
                LOGGER.info(f"File {file['name']} purged from library {library.name} because no actual file was found")
        LOGGER.info("File purge ended")

    @staticmethod
    def get_page(library: LibraryModel, file_data: FileModel, num: int = 0, storage: StorageService = None) -> bytes:
        """Get a specific page with a given number"""
        if not storage:
            storage = StorageService(library)
        return storage.get_page(file_data, FileService.get_opener_lib(file_data.extension), num)

    @staticmethod
    def get_current_page(library: LibraryModel, file: FileModel, storage: StorageService = None):
        """Return file data corresponding to the current page number"""
        return FileService.get_page(library, file, file.current_page, storage)

    @staticmethod
    async def set_page(library: LibraryModel, file: FileModel, num: int) -> FileModel:
        """Set the current page of a file in the database and return the updated FileModel object"""
        if 0 <= num <= file.pages_count - 1:
            return await db_update_file(library.name, str(file.id), UpdateFileModel(
                **{"current_page": num, "update_date": datetime.now()}))
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
