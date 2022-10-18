from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.model.py_object_id import PyObjectId


class LibraryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    path: str = Field(...)
    hidden: bool = Field(...)

    class Config:
        json_encoders = {ObjectId: str}
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed = True
        # Whether an aliased field may be populated by its name as given by the model attribute,
        # as well as the alias (Used to replace "_id" with "id")
        allow_population_by_field_name = True


class UpdateLibraryModel(BaseModel):
    path: Optional[str]
    hidden: Optional[bool]

    class Config:
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed: True
        json_encoders = {ObjectId: str}
