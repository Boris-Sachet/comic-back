import hashlib
import logging
import pathlib
from os import remove, listdir
from os.path import join, isfile
from typing import List, Type, Tuple
from zipfile import ZipFile, BadZipFile
from rarfile import RarFile, NotRarFile, BadRarFile
from pathlib import Path

from PIL.Image import Image
from smb.base import SharedFile
from fastapi.responses import FileResponse

from app.model.file_model import FileModel
from app.services.storage_service import StorageService
from app.tools import is_image

LOGGER = logging.getLogger(__name__)


class StorageServiceLocal(StorageService):
    def calculate_md5(self, file_path: str) -> str:
        md5 = hashlib.md5(pathlib.Path(join(self.library.path, file_path)).read_bytes()).hexdigest()
        LOGGER.debug(f"{file_path} : md5 is {md5}")
        return md5

    def get_opener_lib(self, file_path: str) -> Type[ZipFile | RarFile] | None:
        # Test if file a zip
        try:
            with ZipFile(join(self.library.path, file_path), 'r'):
                return ZipFile
        except BadZipFile:
            pass
        # Test if file is a rar
        try:
            with RarFile(join(self.library.path, file_path), 'r'):
                return RarFile
        except (NotRarFile, BadRarFile):
            pass
        LOGGER.error(f"No opener lib found for {file_path}")

    def list_pages(self, file_path: str, opener_lib: Type[ZipFile | RarFile]) -> List[str]:
        LOGGER.debug(f"{file_path} : Counting pages")
        pages_names = []
        with opener_lib(join(self.library.path, file_path), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    pages_names.append(item.filename)
            LOGGER.debug(f"{file_path} : {len(pages_names)} pages")
            pages_names.sort()
            return pages_names

    def get_page(self, file: FileModel, opener_lib: Type[ZipFile | RarFile], num: int = 0) -> bytes:
        LOGGER.debug(f"{file.full_path} : getting page {num}")
        with opener_lib(join(self.library.path, file.full_path), 'r') as storage_file:
            try:
                with storage_file.open(file.pages_names[num]) as img:
                    return img.read()
            except Exception as e:
                LOGGER.exception(f"{file.full_path} : can't get page {num}", exc_info=e)  # TODO manage the error when files have 0 pages

    def isfile(self, file: str | SharedFile) -> bool:
        return isfile(join(self.library.path, file))

    async def get_dir_content(self, path: str) -> Tuple[List[str], List[str]]:
        dirs = []
        files = []
        for item in listdir(join(self.library.path, path)):
            files.append(item) if isfile(join(self.library.path, join(path, item))) else dirs.append(item)
        return dirs, files

    def get_thumbnail(self, file: FileModel) -> FileResponse:
        """Get the thumbnail image of a file in a ready to send file response object"""
        return FileResponse(self.get_thumbnail_path(file))

    def save_thumbnail(self, file: FileModel, thumbnail: Image):
        try:
            Path(self.thumbnail_folder).mkdir(parents=True, exist_ok=True)
            thumbnail.save(self.get_thumbnail_path(file))
            LOGGER.info(f"Generated thumbnail for {file.id} {file.path}")
        except Exception as e:
            LOGGER.exception(f"Can't save thumbnail for {file.id} {file.full_path} : {e}", exc_info=e)

    def thumbnail_exist(self, file: FileModel) -> bool:
        return self.isfile(join(self.library.path, self.get_thumbnail_path(file)))

    def delete_thumbnail(self, file: FileModel):
        if self.thumbnail_exist(file):
            remove(self.get_thumbnail_path(file))
            LOGGER.info(f"Removed thumbnail for {file.id}")
