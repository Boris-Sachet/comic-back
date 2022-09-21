from rarfile import RarFile

from app.model.file import File
from app.tools import is_image


class Cbr(File):
    def __init__(self, path: str):
        super().__init__(path)
        self.__count_pages()

    def __iter__(self):
        with RarFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    with file.open(item.filename) as img:
                        yield img.read()
            file.close()

    def __count_pages(self):
        with RarFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                if is_image(item.filename):
                    self.pages_names.append(item.filename)
            self.pages_count = len(self.pages_names)

    def get_page(self, num: int = 0):
        """Get a specific page with a given number"""
        with RarFile(self.get_full_path(), 'r') as file:
            with file.open(self.pages_names[num]) as img:
                return img.read()
