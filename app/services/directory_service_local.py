from os import listdir
from os.path import isfile, join
from pathlib import Path

from app.model.library_model import LibraryModel
from app.services.file_service import FileService


class DirectoryServiceLocal:
    connect_type = "local"

    @staticmethod
    def listdir(library: LibraryModel, path: str):
        return listdir(path)

    @staticmethod
    def isfile(library: LibraryModel, path: str, item: str):
        return isfile(FileService.get_full_path(library, join(path, item)))

    @staticmethod
    def get_file_path(path: str, item: str):
        return join(path, item)

    @staticmethod
    def get_suffix(path):
        return Path(path).suffix
