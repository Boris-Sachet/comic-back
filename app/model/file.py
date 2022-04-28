from os.path import basename, join, splitext
from app.endpoint import base_dir
from app.model import TypeModel


class File:

    def __init__(self, path: str):
        self.path = path
        self.name, self.extension = splitext(basename(self.path))
        self.uid = ''
        self.type = TypeModel.FILE

    def get_full_path(self):
        return join(base_dir, self.path)
