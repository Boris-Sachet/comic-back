from zipfile import ZipFile

from app.model.file import File


class Cbz(File):
    def iterfile(self):
        with ZipFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                with file.open(item.filename) as img:
                    yield img.read()

