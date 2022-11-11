from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from app.model.py_object_id import PyObjectId


class LibraryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    path: str = Field(...)
    hidden: bool = Field(...)
    connect_type: str = Field(...)  # smb or local

    @validator('connect_type')
    def connect_type_possible_values(cls, value):
        accepted_values = ["local", "smb"]
        if value not in accepted_values:
            raise ValueError(f"connect_type parameter must be {accepted_values}")
        return value

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
    connect_type: Optional[str]

    @validator('connect_type')
    def connect_type_possible_values(cls, value):
        accepted_values = ["local", "smb"]
        if value not in accepted_values:
            raise ValueError(f"connect_type parameter must be {accepted_values}")
        return value

    class Config:
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed: True
        json_encoders = {ObjectId: str}
