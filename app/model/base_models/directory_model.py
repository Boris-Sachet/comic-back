from os.path import basename

from pydantic import BaseModel, Field

from app.enums.type_model import TypeModel


class DirectoryModel(BaseModel):
    path: str = Field(...)
    name: str = Field(...)
    type: str = TypeModel.DIR.value

    @staticmethod
    def create(path: str):
        return DirectoryModel(**{"path": path, "name": basename(path)})
