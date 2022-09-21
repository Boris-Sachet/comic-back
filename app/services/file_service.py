import pathlib
from os.path import join, isfile

from fastapi import HTTPException

from app.endpoint import base_dir
from app.model.cbz_model import Cbz
from app.model.pdf_model import Pdf


def find_file(path: str):
    "Find the file on the storage and depending on the format, return the proper object"
    file_path = join(base_dir, path)
    if isfile(file_path):
        match pathlib.Path(path).suffix.lower():
            case ".cbz": return Cbz(path=path)
            # case ".pdf": return Pdf(path=path)
            case _: return None
    return None
