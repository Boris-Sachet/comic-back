from pydantic import BaseModel

from app.model import TypeModel


class DirectoryModel(BaseModel):
    name: str
    path: str
    type: TypeModel = TypeModel.DIR

    # def __init__(self, name: str, path: str):
    #     self.name = name
    #     self.path = path
