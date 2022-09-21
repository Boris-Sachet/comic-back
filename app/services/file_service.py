import pathlib
from os.path import join, isfile

from app.endpoint import base_dir
# from app.model.pdf_model import Pdf
from app.model.file import File


def find_file(path: str):
    "Find the file on the storage and depending on the format, return the proper object"
    file_path = join(base_dir, path)
    if isfile(file_path):
        match pathlib.Path(path).suffix.lower():
            case ".cbz": return File(path=path)
            case ".cbr": return File(path=path)
            # case ".pdf": return Pdf(path=path)
            case _: return None
    return None


def execute_action(file: File, action: str):
    """Execute the given reading action on the given reading file"""
    match action:
        case "+": file.next_page()
        case "-": file.prev_page()
        case _: file.set_page(int(action))
