from typing import Tuple, List, Optional

from pydantic import BaseModel

from app.model.file_model import ResponseFileModel
from app.model.directory_model import DirectoryModel


class LibContentResponseModel(BaseModel):
    __root__: Tuple[List[DirectoryModel], List[ResponseFileModel]]


class LibraryResponseModel(BaseModel):
    name: str
    path: str
    hidden: bool
    connect_type: str
    user: Optional[str]
