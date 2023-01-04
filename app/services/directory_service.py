import logging
from os.path import join
from pathlib import Path

from PIL import Image

from app.model.directory_model import DirectoryModel
from app.model.file_model import FileModel
from app.model.library_model import LibraryModel
from app.services.directory_service_local import DirectoryServiceLocal
from app.services.directory_service_smb import DirectoryServiceSmb
from app.services.file_service import FileService

LOGGER = logging.getLogger(__name__)


class DirectoryService:
    _supported_extensions = [".cbz", ".cbr"]
    _factory_list = [DirectoryServiceLocal, DirectoryServiceSmb]

    @staticmethod
    def _select_factory(library: LibraryModel):
        for factory in DirectoryService._factory_list:
            if library.connect_type == factory.connect_type:
                return factory

    @staticmethod
    async def get_dir_content(library: LibraryModel, path: str, generate_thumbnails: bool = False):
        """Return the content of the directory in two list, the list of sub-dirs and the list of supported files
         (as base model extensions)"""
        factory = DirectoryService._select_factory(library)
        return await factory.get_dir_content(library, path, DirectoryService._supported_extensions, generate_thumbnails)

    @staticmethod
    async def scan_in_depth(library: LibraryModel, path: str):
        """Use in depth scanning to go to every folder and sub-folder and analyse the files to make sure they're referenced
        in database or add them if they're not"""
        # Scan base dir
        dirs, files = await DirectoryService.get_dir_content(library, path, True)

        # Scan sub-folders
        for directory in dirs:
            await DirectoryService.scan_in_depth(library, directory.path)

    @staticmethod
    def save_thumbnail(library: LibraryModel, file: FileModel, thumbnail: Image):
        # factory = DirectoryService._select_factory(library)
        try:
            Path(f"{library.path}/.comic-back/thumbnails/").mkdir(parents=True, exist_ok=True)
            thumbnail.save(DirectoryService.get_thumbnail_path(library, file))
            LOGGER.info(f"Generated thumbnail for {file.id} {file.path}")
        except Exception as e:
            LOGGER.error(f"Can't save thumbnail for {file.id} {file.full_path} : {e}")

    @staticmethod
    def thumbnail_exist(library: LibraryModel, file: FileModel):
        factory = DirectoryService._select_factory(library)
        return factory.isfile(library, join(library.path, ".comic-back/thumbnails/"), f"{file.id}.jpg")

    @staticmethod
    def get_thumbnail_path(library: LibraryModel, file: FileModel):
        return f"{library.path}/.comic-back/thumbnails/{file.id}.jpg"
