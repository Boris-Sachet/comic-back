from os.path import join

from app.endpoint import base_dir
from app.model.file_model import FileModel
from PyPDF2 import PdfFileReader


class PdfModel(FileModel):

    def iterfile(self):
        file = PdfFileReader(join(base_dir, self.path))
        page_count = file.getNumPages()

        # for i in range(0, page_count):
