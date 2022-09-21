from zipfile import ZipFile

from app.model.file import File


class Cbz(File):
    def __init__(self, path: str):
        super().__init__(path)
        # self.cover = self.iterfile().__next__()

    def __iter__(self):
        return self.iterfile()

    def iterfile(self):
        with ZipFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                with file.open(item.filename) as img:
                    yield img.read()

