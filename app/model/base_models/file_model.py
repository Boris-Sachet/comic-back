from bson import ObjectId
from pydantic import BaseModel

from app.enums.type_model import TypeModel


class FileModel(BaseModel):
    path: str
    name: str
    extension: str
    type: TypeModel
    pages_count: int
    current_page: int
    md5: str | None

    class Config:
        orm_mode = True
