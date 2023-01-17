import logging
from os.path import join
from pathlib import Path

import smbclient
from PIL import Image
from smbclient import SMBDirEntry

from app.model.directory_model import DirectoryModel
from app.model.file_model import FileModel
from app.model.library_model import LibraryModel
from app.services.file_service import FileService

LOGGER = logging.getLogger(__name__)


class DirectoryServiceSmb:
    connect_type = "smb"
    dir_name_blacklist = ["@eaDir"]

    @staticmethod
    def isfile(library: LibraryModel, path: str, item: SMBDirEntry):
        return item.is_file()

    @staticmethod
    async def get_dir_content(library: LibraryModel, path: str, supported_extensions: list, generate_thumbnails: bool = False):
        """Return the content of the smb directory in two list, the list of subdirs and the list of supported files
             (as base model extensions)"""
        dirs = []
        files = []
        smb_info = {"username": library.user, "password": library.password}
        for item in smbclient.scandir(path=FileService.get_full_path(library, path), **smb_info):
            if item.is_file():
                if Path(item.name).suffix in supported_extensions:
                    if (db_file := await FileService.get_file_from_db(library, path + '\\' + item.name)) is not None:
                        files.append(db_file)
                        if generate_thumbnails and not DirectoryServiceSmb.thumbnail_exist(library, db_file):
                            thumbnail = FileService.generate_thumbnail_cover(library, db_file)
                            DirectoryServiceSmb.save_thumbnail(library, db_file, thumbnail)
            else:
                if (not item.name.startswith('.')) or (item not in DirectoryServiceSmb.dir_name_blacklist):
                    dirs.append(DirectoryModel.create(join(path, item.name)))
        return dirs, files

    @staticmethod
    def save_thumbnail(library: LibraryModel, file: FileModel, thumbnail: Image):
        # TODO
        # try:
        #     Path(f"{library.path}/.comic-back/thumbnails/").mkdir(parents=True, exist_ok=True)
        #     thumbnail.save(DirectoryServiceSmb.get_thumbnail_path(library, file))
        #     LOGGER.info(f"Generated thumbnail for {file.id} {file.path}")
        # except Exception as e:
        #     LOGGER.error(f"Can't save thumbnail for {file.id} {file.full_path} : {e}")
        pass

    @staticmethod
    def thumbnail_exist(library: LibraryModel, file: FileModel) -> bool:
        # TODO
        # return isfile(FileService.get_full_path(library, join(".comic-back/thumbnails/", f"{file.id}.jpg")))
        pass

    @staticmethod
    def get_thumbnail_path(library: LibraryModel, file: FileModel) -> str:
        # TODO
        # return f"{library.path}\\.comic-back\\thumbnails\\{file.id}.jpg"
        pass

    @staticmethod
    def delete_thumbnail(library: LibraryModel, file: FileModel):
        # TODO
        # if DirectoryServiceSmb.thumbnail_exist(library, file):
        #     remove(DirectoryServiceSmb.get_thumbnail_path(library, file))
        pass
