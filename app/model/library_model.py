from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator, root_validator

from app.model.py_object_id import PyObjectId


class LibraryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    path: str = Field(...)
    hidden: bool = Field(...)
    connect_type: str = Field(...)  # smb or local
    server: Optional[str]
    service_name: Optional[str]
    user: Optional[str]
    password: Optional[str]

    @validator("path")
    def trim_path(cls, value: str):
        if value.endswith("\\") or value.endswith("/"):
            return value.rstrip(value[-1])
        return value

    @validator('connect_type')
    def connect_type_possible_values(cls, value):
        accepted_values = ["local", "smb"]
        if value not in accepted_values:
            raise ValueError(f"connect_type parameter must be {accepted_values}")
        return value

    @root_validator
    def check_smb_fields(cls, values):
        if values.get("connect_type") == "smb":
            if values.get("server") is None:
                raise ValueError("Server address required for SMB connection")
            if values.get("service_name") is None:
                raise ValueError("Share name required for SMB connection")
            if values.get("user") is None or values.get("password") is None:
                raise ValueError("User and password required for SMB connection")
        return values

    def smb_conn_info(self) -> dict:
        return {
            "username": self.user,
            "password": self.password,
            "my_name": "comic-back",
            "remote_name": self.server,
            "use_ntlm_v2": True
        }

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
    user: Optional[str]
    password: Optional[str]

    @validator('connect_type')
    def connect_type_possible_values(cls, value):
        accepted_values = ["local", "smb"]
        if value not in accepted_values:
            raise ValueError(f"connect_type parameter must be {accepted_values}")
        return value

    @root_validator
    def check_smb_user_pwd(cls, values):
        if values.get("connect_type") == "smb":
            if values.get("user") is None or values.get("password") is None:
                raise ValueError("User and password required for SMB connection")
        return values

    class Config:
        # Whether to allow arbitrary user types for fields
        # (they are validated simply by checking if the value is an instance of the type)
        arbitrary_types_allowed: True
        json_encoders = {ObjectId: str}
