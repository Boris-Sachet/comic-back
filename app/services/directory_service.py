import pathlib
from os import listdir
from os.path import isfile, join

from app.endpoint import base_dir
from app.model.base_models.file_model import FileModel
from app.model.directory import Directory
from app.model.file import File


def get_dir_content(path: str):
    """Return the content of the directory in two list, the list of subdirs and the list of supported files
     (as base model extensions)"""
    dirs = []
    files = []
    for item in listdir(base_dir + path):
        if isfile(join(base_dir, path, item)):
            match pathlib.Path(item).suffix:
                case ".cbz": files.append(FileModel.from_orm(File(path=join(path, item))))
                case ".cbr": files.append(FileModel.from_orm(File(path=join(path, item))))
                # case _: files.append(FileModel.from_orm(File(path=join(path, item))))
        else:
            dirs.append(Directory(path=join(path, item)))
    return dirs, files
