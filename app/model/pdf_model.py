import fitz

from os.path import join

from app.endpoint import base_dir
from app.model.file import File


class Pdf(File):

    def __iter__(self):
        """Try to render page by page with PyMuPDF https://pymupdf.readthedocs.io/en/latest/tutorial.html#rendering-a-page
         No great success here
         previous test was with PdfFileReader from PyPDF2, maybe try again?"""
        file = fitz.Document(join(base_dir, self.path))

        for i in range(0, file.page_count):
            page = file.load_page(i)
            test = page.get_pixmap()
            yield page.get_pixmap()
