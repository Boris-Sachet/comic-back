from os import listdir
from os.path import isfile, join
from pathlib import Path

from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.file_service import FileService


class DirectoryServiceLocal:
    connect_type = "local"

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
                        # if generate_thumbnails and not DirectoryService.thumbnail_exist(library, db_file):
                        #     thumbnail = FileService.generate_thumbnail_cover(library, db_file)
                        #     DirectoryService.save_thumbnail(library, db_file, thumbnail)
            else:
                if not item.startswith('.'):
                    dirs.append(DirectoryModel.create(join(path, item)))
        return dirs, files
