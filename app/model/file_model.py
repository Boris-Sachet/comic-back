from os.path import basename, join

from pydantic import BaseModel

from app.endpoint import base_dir
from app.model import TypeModel


class FileModel(BaseModel):
    path: str
    name: str
    # uid: str
    # type: TypeModel = TypeModel.FILE

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.name = basename(self.path)

    def get_full_path(self):
        return join(base_dir, self.path)
