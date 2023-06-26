import logging
from os.path import join
from pathlib import Path
from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.db_service import db_find_first_child_in_path
from app.services.file_service import FileService
from app.services.storage_service import StorageService

LOGGER = logging.getLogger(__name__)


class DirectoryService:
    __supported_extensions = [".cbz", ".cbr"]
    __dir_name_blacklist = [".", "..", "@eaDir"]

    @classmethod
    async def get_dir_content(cls, library: LibraryModel, path: str, generate_thumbnails: bool = False,
                              storage: StorageService = None, dir_thumbnail: bool = False):
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
            if (not directory.startswith('.')) and (directory not in cls.__dir_name_blacklist):
                LOGGER.debug(f"Found directory : {join(path, directory)}")
                dir_model = DirectoryModel.create(join(path, directory))
                if dir_thumbnail:
                    dir_model.thumbnail_id = await DirectoryService.get_dir_thumbnail(library, dir_model)
                dirs.append(dir_model)

        # Files list building
        for file in storage_files:
            if Path(file).suffix in cls.__supported_extensions:
                if (db_file := await FileService.get_file_from_db(library, join(path, file), storage)) is not None:
                    LOGGER.debug(f"Found file : {db_file.full_path}")
                    files.append(db_file)
                    # Thumbnail management if needed
                    if generate_thumbnails and not storage.thumbnail_exist(db_file):
                        thumbnail = FileService.generate_thumbnail_cover(library, db_file, storage)
                        if thumbnail:
                            storage.save_thumbnail(db_file, thumbnail)
        LOGGER.info(f"Get dir content found {len(files)} files and {len(dirs)} directories in {path} of library {library}")
        return dirs, files

    @classmethod
    async def scan_in_depth(cls, library: LibraryModel, path: str, storage: StorageService = None):
        """
        Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
        in database or add them if they're not
        """
        if not storage:
            storage = StorageService(library)
        # Scan base dir
        dirs, files = await DirectoryService.get_dir_content(library, path, True, storage)

        # Scan sub-folders
        for directory in dirs:
            await DirectoryService.scan_in_depth(library, directory.path, storage=storage)

    @classmethod
    async def get_dir_thumbnail(cls, library: LibraryModel, dir_model: DirectoryModel) -> str | None:
        """Get the id of the first child of the folder"""
        file = await db_find_first_child_in_path(library.name, dir_model.path)
        if file:
            return str(file.id)
        return None
