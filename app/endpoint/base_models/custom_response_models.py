from typing import Tuple, List

from pydantic import BaseModel

from app.model.base_models.file_model import FileModel
from app.model.base_models.directory_model import DirectoryModel


class DirContentResponseModel(BaseModel):
    __root__: Tuple[List[DirectoryModel], List[FileModel]]
