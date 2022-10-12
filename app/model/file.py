import hashlib
import pathlib
from os.path import basename, join, splitext
from zipfile import ZipFile

from rarfile import RarFile

from app.endpoint import base_dir
from app.enums.type_model import TypeModel
from app.tools import is_image


class File:
    """
    Main class of a comic file
    Note: when all files are listed in a dir a lot of File object can be created, there's a possibility that
    the counting of pages at init is going to cause performances issues when displaying big directories
    """
    def __init__(self, path: str):
        self.path = path
        self.name, self.extension = splitext(basename(self.path))
        self.type = TypeModel.FILE
        self.pages_count = 0
        self.pages_names = []
        self.__opener_lib = self.__get_opener_lib()  # TODO test if jsonable_encoder() ignores private params, test it with __ and _
        self.__count_pages()
        self.current_page = 0
        self.md5 = None

    def __iter__(self):
        with self.__opener_lib(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                with file.open(item.filename) as img:
                    yield img.read()
            file.close()

    def __count_pages(self):
        """Create a list of all the pages names in their naming order and count the result"""
        with self.__opener_lib(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    self.pages_names.append(item.filename)
            self.pages_count = len(self.pages_names)

    def __get_opener_lib(self):
        """Find the library needed to open the file based on it's extension"""
        match self.extension.lower():
            case ".cbz":
                return ZipFile
            case ".cbr":
                return RarFile

    def calculate_md5(self):
        self.md5 = hashlib.md5(pathlib.Path(self.get_full_path()).read_bytes()).hexdigest()
        return self.md5

    def get_full_path(self):
        return join(base_dir, self.path)

    def get_page(self, num: int = 0):
        """Get a specific page with a given number"""
        with self.__opener_lib(self.get_full_path(), 'r') as file:
            with file.open(self.pages_names[num]) as img:
                return img.read()

    def get_current_page(self):
        return self.get_page(self.current_page)

    # Possible reading actions on this object
    def next_page(self):
        if self.current_page < self.pages_count - 1:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1

    def set_page(self, num: int):
        if 0 <= num <= self.pages_count - 1:
            self.current_page = num
