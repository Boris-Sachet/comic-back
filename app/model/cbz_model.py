from zipfile import ZipFile

from app.model.file_model import FileModel


class CbzModel(FileModel):
    def iterfile(self):
        with ZipFile(self.get_full_path(), 'r') as file:
            for item in file.infolist():
                with file.open(item.filename) as img:
                    yield img.read()

