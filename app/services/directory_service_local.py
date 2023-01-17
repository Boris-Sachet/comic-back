import logging
from os import listdir, remove
from os.path import isfile, join
from pathlib import Path

from PIL import Image

from app.model.directory_model import DirectoryModel
from app.model.file_model import FileModel
from app.model.library_model import LibraryModel
from app.services.file_service import FileService

LOGGER = logging.getLogger(__name__)


class DirectoryServiceLocal:
    connect_type = "local"
    dir_name_blacklist = ["@eaDir"]

    @staticmethod
    def isfile(library: LibraryModel, path: str, item: str):
        return isfile(FileService.get_full_path(library, join(path, item)))

    @staticmethod
    async def get_dir_content(library: LibraryModel, path: str, supported_extentions: list, generate_thumbnails: bool = False):
        """Return the content of the local directory in two list, the list of subdirs and the list of supported files
             (as base model extensions)"""
        dirs = []
        files = []
        for item in listdir(FileService.get_full_path(library, path)):
            if isfile(FileService.get_full_path(library, join(path, item))):
                if Path(item).suffix in supported_extentions:
                    if (db_file := await FileService.get_file_from_db(library, join(path, item))) is not None:
                        files.append(db_file)
                        if generate_thumbnails and not DirectoryServiceLocal.thumbnail_exist(library, db_file):
                            thumbnail = FileService.generate_thumbnail_cover(library, db_file)
                            DirectoryServiceLocal.save_thumbnail(library, db_file, thumbnail)
            else:
                if (not item.startswith('.')) and (item not in DirectoryServiceLocal.dir_name_blacklist):
                    dirs.append(DirectoryModel.create(join(path, item)))
        return dirs, files

    @staticmethod
    def save_thumbnail(library: LibraryModel, file: FileModel, thumbnail: Image):
        try:
            Path(f"{library.path}/.comic-back/thumbnails/").mkdir(parents=True, exist_ok=True)
            thumbnail.save(DirectoryServiceLocal.get_thumbnail_path(library, file))
            LOGGER.info(f"Generated thumbnail for {file.id} {file.path}")
        except Exception as e:
            LOGGER.error(f"Can't save thumbnail for {file.id} {file.full_path} : {e}")

    @staticmethod
    def thumbnail_exist(library: LibraryModel, file: FileModel) -> bool:
        return isfile(FileService.get_full_path(library, join(".comic-back/thumbnails/", f"{file.id}.jpg")))

    @staticmethod
    def get_thumbnail_path(library: LibraryModel, file: FileModel) -> str:
        return f"{library.path}/.comic-back/thumbnails/{file.id}.jpg"

    @staticmethod
    def delete_thumbnail(library: LibraryModel, file: FileModel):
        if DirectoryServiceLocal.thumbnail_exist(library, file):
            remove(DirectoryServiceLocal.get_thumbnail_path(library, file))
