from bson import ObjectId
from fastapi import HTTPException

from app.database_connect import db
from app.model.base_models.file_model import FileModel, UpdateFileModel
from app.services import Collections


async def search_by_id(object_id: str, collection: Collections):
    return await db[collection.value].find_one({"_id": ObjectId(object_id)})


async def update_by_id(object_id: str, collection: Collections, dict_data: {}):
    return await db[collection.value].update_one({"_id": ObjectId(object_id)}, {"$set": dict_data})


async def insert_one(collection: Collections, dict_data: {}):
    return await db[collection.value].insert_one(dict_data)


async def get_list(collection: Collections):
    return await db[collection.value].find().to_list(None)


async def delete_by_id(object_id: str, collection: Collections):
    return await db[collection.value].delete_one({"_id": ObjectId(object_id)})


async def search_with_attributes(attributes: {}, collection: Collections):
    return await db[collection.value].find_one(attributes)


async def search_many_with_attributes(attributes: {}, collection: Collections):
    return await db[collection.value].find(attributes).to_list(None)


# FILE SPECIFIC METHODS
async def find_file(object_id: str) -> FileModel | None:
    file_dict = await db[Collections.COMICS.value].find_one({"_id": ObjectId(object_id)})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def find_file_by_full_path(file_path: str) -> FileModel | None:
    file_dict = await db[Collections.COMICS.value].find_one({"full_path": file_path})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def find_file_by_md5(md5: str) -> FileModel | None:
    file_dict = await db[Collections.COMICS.value].find_one({"md5": md5})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def insert_file(file: FileModel):
    return await db[Collections.COMICS.value].insert_one(file.dict(by_alias=True))


async def update_file(object_id: str, file: UpdateFileModel) -> FileModel:
    file = {key: value for key, value in file.dict().items() if value is not None}

    if len(file) >= 1:
        update_result = await db[Collections.COMICS.value].update_one({"_id": ObjectId(object_id)}, {"$set": file})
        if update_result.modified_count == 1:
            if (updated_file := await find_file(object_id)) is not None:
                return updated_file

    if (updated_file := await find_file(object_id)) is not None:
        return updated_file

    raise HTTPException(status_code=404, detail=f"File {object_id} not found")


async def delete_file(object_id: str):
    return await db[Collections.COMICS.value].delete_one({"_id": ObjectId(object_id)})
