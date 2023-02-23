import logging
from os.path import join
from pathlib import Path
from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.file_service import FileService
from app.services.storage_service import StorageService

LOGGER = logging.getLogger(__name__)


class DirectoryService:
    __supported_extensions = [".cbz", ".cbr"]
    __dir_name_blacklist = [".", "..", "@eaDir"]

    @staticmethod
    async def get_dir_content(library: LibraryModel, path: str, generate_thumbnails: bool = False, storage: StorageService = None):
        """Return the content of the directory in two list, the list of sub-dirs and the list of supported files
         (as base model extensions)"""
        dirs = []
        files = []
        if not storage:
            storage = StorageService(library)
        LOGGER.debug(f"Getting content of folder : {path}")
        storage_dirs, storage_files = await storage.get_dir_content(path)
        # Directory list building
        for directory in storage_dirs:
            if (not directory.startswith('.')) and (directory not in DirectoryService.__dir_name_blacklist):
                LOGGER.debug(f"Found directory : {join(path, directory)}")
                dirs.append(DirectoryModel.create(join(path, directory)))

        # Files list building
        for file in storage_files:
            if Path(file).suffix in DirectoryService.__supported_extensions:
                if (db_file := await FileService.get_file_from_db(library, join(path, file), storage)) is not None:
                    LOGGER.debug(f"Found file : {db_file.full_path}")
                    files.append(db_file)
                    # Thumbnail management if needed
                    if generate_thumbnails and not storage.thumbnail_exist(db_file):
                        thumbnail = FileService.generate_thumbnail_cover(library, db_file, storage)
                        if thumbnail:
                            storage.save_thumbnail(db_file, thumbnail)
        return dirs, files

    @staticmethod
    async def scan_in_depth(library: LibraryModel, path: str, storage: StorageService = None):
        """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
        in database or add them if they're not"""
        if not storage:
            storage = StorageService(library)
        # Scan base dir
        dirs, files = await DirectoryService.get_dir_content(library, path, True, storage)

        # Scan sub-folders
        for directory in dirs:
            await DirectoryService.scan_in_depth(library, directory.path, storage=storage)
