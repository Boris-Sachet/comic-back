import hashlib
import pathlib
from os.path import basename, join, splitext
from zipfile import ZipFile

from rarfile import RarFile

from app.endpoint import base_dir
from app.enums.type_model import TypeModel
from app.tools import is_image


class File:

    def __init__(self, path: str):
        self.path = path
        self.name, self.extension = splitext(basename(self.path))
        # self.uid = hashlib.md5(pathlib.Path(self.get_full_path()).read_bytes()).hexdigest()
        self.type = TypeModel.FILE
        self.pages_count = 0
        self.pages_names = []
        self.current_page = 0
        match self.extension.lower():
            case "cbz" : self.opener_lib = ZipFile
            case "cbr" : self.opener_lib = RarFile

    def __iter__(self):
        with ZipFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                with file.open(item.filename) as img:
                    yield img.read()
            file.close()

    def __count_pages(self):
        """Create a list of all the pages names in their naming order and count the result"""
        with ZipFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    self.pages_names.append(item.filename)
            self.pages_count = len(self.pages_names)

    def get_full_path(self):
        return join(base_dir, self.path)

    def get_page(self, num: int = 0):
        """Get a specific page with a given number"""
        with self.opener_lib(self.get_full_path(), 'r') as file:
            with file.open(self.pages_names[num]) as img:
                return img.read()
