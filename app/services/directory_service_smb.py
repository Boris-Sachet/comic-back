from os.path import join
from pathlib import Path

import smbclient
from smbclient import SMBDirEntry

from app.model.directory_model import DirectoryModel
from app.model.library_model import LibraryModel
from app.services.file_service import FileService


class DirectoryServiceSmb:
    connect_type = "smb"

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
                        # if generate_thumbnails and not DirectoryService.thumbnail_exist(library, db_file):
                        #     thumbnail = FileService.generate_thumbnail_cover(library, db_file)
                        #     DirectoryService.save_thumbnail(library, db_file, thumbnail)
            else:
                dirs.append(DirectoryModel.create(join(path, item.name)))
        return dirs, files
