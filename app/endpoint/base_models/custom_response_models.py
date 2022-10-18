from typing import Tuple, List

from pydantic import BaseModel

from app.model.file_model import FileModel
from app.model.directory_model import DirectoryModel


class LibContentResponseModel(BaseModel):
    __root__: Tuple[List[DirectoryModel], List[FileModel]]
