import hashlib
import logging
import os.path
from io import BytesIO
from os.path import join
from typing import Type, List, Tuple
from zipfile import ZipFile, BadZipFile

from PIL.Image import Image
from rarfile import RarFile, NotRarFile, BadRarFile
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile
from smb.smb_structs import OperationFailure
from starlette.responses import Response

from app.model.file_model import FileModel
from app.services.storage_service import StorageService
from app.tools import is_image

LOGGER = logging.getLogger(__name__)


class StorageServiceSmb(StorageService):
    __con: SMBConnection = None

    def __get_smb_conn(self) -> SMBConnection:
        if self.__con is None:
            conn = SMBConnection(**self.library.smb_conn_info())
            conn.connect(self.library.server, 445)
            self.__con = conn
        return self.__con

    def __ensure_directory_exist(self, conn: SMBConnection, path: str):
        try:
            conn.listPath(service_name=self.library.service_name, path=path)
            return True
        except OperationFailure:
            parent_dir, child_dir = os.path.split(path)
            self.__ensure_directory_exist(conn, parent_dir)
            conn.createDirectory(service_name=self.library.service_name, path=path)
            return True
        return False

    def calculate_md5(self, file_path: str) -> str:
        with BytesIO() as file_io:
            conn = self.__get_smb_conn()
            conn.retrieveFile(service_name=self.library.service_name, path=join(self.library.path, file_path), file_obj=file_io)
            file_io.seek(0)
            hasher = hashlib.md5()
            while True:
                chunk = file_io.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
            LOGGER.debug(f"{file_path} : md5 is {hasher.hexdigest()}")
            return hasher.hexdigest()

    def get_opener_lib(self, file_path: str) -> Type[ZipFile | RarFile] | None:
        conn = self.__get_smb_conn()
        with BytesIO() as file_io:
            conn.retrieveFile(service_name=self.library.service_name, path=join(self.library.path, file_path), file_obj=file_io)
            file_io.seek(0)
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
        conn = self.__get_smb_conn()
        with BytesIO() as file_io:
            conn.retrieveFile(service_name=self.library.service_name, path=join(self.library.path, file_path), file_obj=file_io)
            file_io.seek(0)
            # Open the file from the BytesIO object
            with opener_lib(file_io, 'r') as file:
                for item in file.infolist():
                    if is_image(item.filename):
                        pages_names.append(item.filename)
                LOGGER.debug(f"{file_path} : {len(pages_names)} pages")
                pages_names.sort()
                return pages_names

    def get_page(self, file: FileModel, opener_lib: Type[ZipFile | RarFile], num: int = 0) -> bytes:
        LOGGER.debug(f"{file.full_path} : getting page {num}")
        conn = self.__get_smb_conn()
        with BytesIO() as file_io:
            conn.retrieveFile(service_name=self.library.service_name, path=join(self.library.path, file.full_path), file_obj=file_io)
            file_io.seek(0)
            # Open the file from the BytesIO object
            with opener_lib(file_io, 'r') as storage_file:
                try:
                    with storage_file.open(file.pages_names[num]) as img:
                        return img.read()
                except Exception as e:
                    LOGGER.exception(f"{file.full_path} : can't get page {num}", exc_info=e)  # TODO manage the error when files have 0 pages

    def isfile(self, file: str | SharedFile) -> bool:
        if type(file) == SharedFile:
            return not file.isDirectory
        parent_dir, file_name = os.path.split(file)
        conn = self.__get_smb_conn()
        files_list = conn.listPath(service_name=self.library.service_name, path=join(self.library.path, parent_dir))
        return any((not listed_file.isDirectory) and listed_file.filename == file_name for listed_file in files_list)

    async def get_dir_content(self, path: str) -> Tuple[List[str], List[str]]:
        dirs = []
        files = []
        conn = self.__get_smb_conn()
        for item in conn.listPath(service_name=self.library.service_name, path=join(self.library.path, path)):
            files.append(item.filename) if not item.isDirectory else dirs.append(item.filename)
        return dirs, files

    def get_thumbnail(self, file: FileModel) -> Response:
        """Get the thumbnail image of a file in a ready to send file response object"""
        conn = self.__get_smb_conn()
        with BytesIO() as file_io:
            conn.retrieveFile(service_name=self.library.service_name, path=self.get_thumbnail_path(file),
                              file_obj=file_io)
            file_io.seek(0)
            content = file_io.read()
            return Response(content=content, media_type="image/jpeg",
                            headers={"Content-Length": str(len(content)), "Content-Encoding": "binary"})

    def save_thumbnail(self, file: FileModel, thumbnail: Image):
        conn = self.__get_smb_conn()
        img_io = BytesIO()
        try:
            self.__ensure_directory_exist(conn, self.thumbnail_folder)
            thumbnail.save(img_io, "JPEG")
            img_io.seek(0)
            conn.storeFile(service_name=self.library.service_name,
                           path=self.get_thumbnail_path(file),
                           file_obj=img_io)
            LOGGER.info(f"Saved thumbnail for {file.id} {file.full_path}")
        except Exception as e:
            LOGGER.exception(f"Can't save thumbnail for {file.id} {file.full_path} : {e}", exc_info=e)

    def thumbnail_exist(self, file: FileModel) -> bool:
        conn = self.__get_smb_conn()
        self.__ensure_directory_exist(conn, self.thumbnail_folder)
        thumbnails = conn.listPath(service_name=self.library.service_name, path=self.thumbnail_folder)
        return any(thumbnail.filename == f"{file.id}.jpg" for thumbnail in thumbnails)

    def delete_thumbnail(self, file: FileModel):
        if self.thumbnail_exist(file):
            conn = self.__get_smb_conn()
            conn.deleteFiles(self.library.service_name, self.get_thumbnail_path(file))
            LOGGER.info(f"Removed thumbnail for {file.id}")
