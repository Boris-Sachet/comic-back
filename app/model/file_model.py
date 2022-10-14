import os
from os.path import splitext, basename
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field

from app.model.py_object_id import PyObjectId


class FileModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    full_path: str = Field(...)
    path: str = Field(...)
    name: str = Field(...)
    extension: str = Field(...)
    type: str = Field(...)
    pages_count: int = Field(...)
    pages_names: List[str] = Field(...)
    current_page: int = Field(...)
    md5: str = Field(...)

    class Config:
        json_encoders = {ObjectId: str}
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed = True
        # Whether an aliased field may be populated by its name as given by the model attribute,
        # as well as the alias (Used to replace "_id" with "id")
        allow_population_by_field_name = True


class UpdateFileModel(BaseModel):
    full_path: Optional[str]
    path: Optional[str]
    name: Optional[str]
    extension: Optional[str]
    pages_count: Optional[int]
    pages_names: Optional[List[str]]
    current_page: Optional[int]
    md5: Optional[str]

    class Config:
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed: True
        json_encoders = {ObjectId: str}

    @staticmethod
    def update_path(file_path):
        name, extension = splitext(basename(file_path))
        update_file_dict = {
            "full_path": file_path,
            "path": os.path.dirname(file_path),
            "name": name,
            "extension": extension
        }
        return UpdateFileModel(**update_file_dict)
