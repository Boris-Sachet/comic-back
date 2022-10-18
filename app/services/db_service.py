from typing import List

from bson import ObjectId
from fastapi import HTTPException

from app.database_connect import db
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel, UpdateLibraryModel
from app.services import Collections


# async def search_by_id(object_id: str, collection: Collections):
#     return await db[collection.value].find_one({"_id": ObjectId(object_id)})
#
#
# async def update_by_id(object_id: str, collection: Collections, dict_data: {}):
#     return await db[collection.value].update_one({"_id": ObjectId(object_id)}, {"$set": dict_data})
#
#
# async def insert_one(collection: Collections, dict_data: {}):
#     return await db[collection.value].insert_one(dict_data)
#
#
# async def get_list(collection: Collections):
#     return await db[collection.value].find().to_list(None)
#
#
# async def delete_by_id(object_id: str, collection: Collections):
#     return await db[collection.value].delete_one({"_id": ObjectId(object_id)})
#
#
# async def search_with_attributes(attributes: {}, collection: Collections):
#     return await db[collection.value].find_one(attributes)
#
#
# async def search_many_with_attributes(attributes: {}, collection: Collections):
#     return await db[collection.value].find(attributes).to_list(None)

# =====================
# FILE SPECIFIC METHODS
# =====================
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

    # If there is modifications to do
    if len(file) >= 1:
        update_result = await db[Collections.COMICS.value].update_one({"_id": ObjectId(object_id)}, {"$set": file})
        if update_result.modified_count == 1:
            if (updated_file := await find_file(object_id)) is not None:
                return updated_file

    # No modification to do or update failed
    if (file := await find_file(object_id)) is not None:
        return file

    raise HTTPException(status_code=404, detail=f"File {object_id} not found")


async def delete_file(object_id: str):
    return await db[Collections.COMICS.value].delete_one({"_id": ObjectId(object_id)})


# ========================
# LIBRARY SPECIFIC METHODS
# ========================
async def db_find_library(object_id: str) -> LibraryModel | None:
    library_dict = await db[Collections.LIBRARIES.value].find_one({"_id": ObjectId(object_id)})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_library_by_name(name: str) -> LibraryModel | None:
    library_dict = await db[Collections.LIBRARIES.value].find_one({"name": name})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_all_libraries() -> List[LibraryModel]:
    return await db[Collections.LIBRARIES.value].find().to_list(None)


async def db_insert_library(library: LibraryModel):
    return await db[Collections.LIBRARIES.value].insert_one(library.dict(by_alias=True))


async def db_update_library(object_id: str, library: UpdateLibraryModel) -> LibraryModel:
    library = {key: value for key, value in library.dict().items() if value is not None}

    # If there is modifications to do
    if len(library) >= 1:
        update_result = await db[Collections.LIBRARIES.value].update_one({"_id": ObjectId(object_id)}, {"$set": library})
        if update_result.modified_count == 1:
            if (updated_library := await db_find_library(object_id)) is not None:
                return updated_library

    # No modification to do or update failed
    if (library := await db_find_library(object_id)) is not None:
        return library

    raise HTTPException(status_code=404, detail=f"Library {object_id} not found")


async def db_delete_library(object_id: str):
    return await db[Collections.LIBRARIES.value].delete_one({"_id": ObjectId(object_id)})
