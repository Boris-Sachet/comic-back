from pathlib import Path

import smbclient
from smbclient import SMBDirEntry

from app.model.library_model import LibraryModel


class DirectoryServiceSmb:
    connect_type = "smb"

    @staticmethod
    def listdir(library: LibraryModel, path: str):
        smb_info = {"username": library.user, "password": library.password}
        return smbclient.scandir(path=path, **smb_info)

    @staticmethod
    def isfile(library: LibraryModel, path: str, item: SMBDirEntry):
        return item.is_file()

    @staticmethod
    def get_file_path(path: str, item: SMBDirEntry):
        return path + '\\' + item.name

    @staticmethod
    def get_suffix(item: SMBDirEntry):
        return Path(item.name).suffix
