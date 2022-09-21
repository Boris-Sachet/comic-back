import hashlib
import pathlib
from os.path import basename, join, splitext
from app.endpoint import base_dir
from app.model import TypeModel


class File:

    def __init__(self, path: str):
        self.path = path
        self.name, self.extension = splitext(basename(self.path))
        # self.uid = hashlib.md5(pathlib.Path(self.get_full_path()).read_bytes()).hexdigest()
        self.type = TypeModel.FILE

    def get_full_path(self):
        return join(base_dir, self.path)
