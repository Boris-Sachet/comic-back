import importlib
from abc import ABC, abstractmethod
from typing import List, Type, Tuple
from zipfile import ZipFile

from PIL.Image import Image
from rarfile import RarFile
from smb.base import SharedFile
from starlette.responses import Response

from app.model.file_model import FileModel
from app.model.library_model import LibraryModel


# class StorageService(ABC):
class StorageService:
    def __init__(self, library: LibraryModel):
        """Replace this class by a children class according to library connect_type"""
        module = importlib.import_module("app.services.storage_service_" + library.connect_type)
        self.__class__ = getattr(module, "StorageService" + library.connect_type.capitalize())
        self.library = library
        self.thumbnail_folder = f"{self.library.path}/.comic-back/thumbnails"

    def get_thumbnail_path(self, file: FileModel) -> str:
        return f"{self.thumbnail_folder}/{file.id}.jpg"

    # Files methods
    # @abstractmethod
    def calculate_md5(self, file_path: str) -> str:
        """Calculate md5 signature of a file"""
        pass

    def get_opener_lib(self, file_path: str) -> Type[ZipFile | RarFile] | None:
        """Test the file directly to see which library can open it"""
        pass

    # @abstractmethod
    def list_pages(self, file_path: str, opener_lib: Type[ZipFile | RarFile]) -> List[str]:
        """Create a sorted list of all the pages names in their naming order and count the result"""
        pass

    # @abstractmethod
    def get_page(self, file: FileModel, opener_lib: Type[ZipFile | RarFile], num: int = 0) -> bytes:
        """Get a specific page with a given number"""
        pass

    # Directory methods
    # @abstractmethod
    def isfile(self, file: str | SharedFile) -> bool:
        """Determine if item at given path if a file"""
        pass

    # @abstractmethod
    async def get_dir_content(self, path: str) -> Tuple[List[str], List[str]]:
        """Return the content of a directory in two lists, the list of sub-dirs and the list of supported files"""
        pass

    # Thumbnails methods
    # @abstractmethod
    def get_thumbnail(self, file: FileModel) -> Response:
        """Get the thumbnail image of a file in a ready to send file response object"""
        pass

    # @abstractmethod
    def save_thumbnail(self, file: FileModel, thumbnail: Image):
        """Save a thumbnail image in the library storage"""
        pass

    # @abstractmethod
    def thumbnail_exist(self, file: FileModel) -> bool:
        """Check if a thumbnail exist for the given file"""
        pass

    # @abstractmethod
    def delete_thumbnail(self, file: FileModel):
        """Delete the thumbnail for the given file"""
        pass
