from typing import List

from bson import ObjectId
from fastapi import HTTPException

from app.database_connect import db
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel, UpdateLibraryModel


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

# ===========================
# COLLECTION SPECIFIC METHODS
# ===========================
async def db_remove_collection(collection_name: str):
    return await db[collection_name].drop()


# =====================
# FILE SPECIFIC METHODS
# =====================
async def find_file(library_name: str, object_id: str) -> FileModel | None:
    file_dict = await db[library_name].find_one({"_id": ObjectId(object_id)})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def find_file_by_full_path(library_name: str, file_path: str) -> FileModel | None:
    file_dict = await db[library_name].find_one({"full_path": file_path})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def find_file_by_md5(library_name: str, md5: str) -> FileModel | None:
    file_dict = await db[library_name].find_one({"md5": md5})
    if file_dict is not None:
        return FileModel(**file_dict)
    return None


async def insert_file(library_name: str, file: FileModel):
    return await db[library_name].insert_one(file.dict(by_alias=True))


async def update_file(library_name: str, object_id: str, file: UpdateFileModel) -> FileModel:
    file = {key: value for key, value in file.dict().items() if value is not None}

    # If there is modifications to do
    if len(file) >= 1:
        update_result = await db[library_name].update_one({"_id": ObjectId(object_id)}, {"$set": file})
        if update_result.modified_count == 1:
            if (updated_file := await find_file(library_name, object_id)) is not None:
                return updated_file

    # No modification to do or update failed
    if (file := await find_file(library_name, object_id)) is not None:
        return file

    raise HTTPException(status_code=404, detail=f"File {object_id} not found")


async def delete_file(library_name: str, object_id: str):
    return await db[library_name].delete_one({"_id": ObjectId(object_id)})


# ========================
# LIBRARY SPECIFIC METHODS
# ========================
LIBRARIES = "libraries"


async def db_find_library(object_id: str) -> LibraryModel | None:
    library_dict = await db[LIBRARIES].find_one({"_id": ObjectId(object_id)})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_library_by_name(name: str) -> LibraryModel | None:
    library_dict = await db[LIBRARIES].find_one({"name": name})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_all_libraries() -> List[LibraryModel]:
    return await db[LIBRARIES].find().to_list(None)


async def db_insert_library(library: LibraryModel):
    return await db[LIBRARIES].insert_one(library.dict(by_alias=True))


async def db_update_library(object_id: str, library: UpdateLibraryModel) -> LibraryModel:
    library = {key: value for key, value in library.dict().items() if value is not None}

    # If there is modifications to do
    if len(library) >= 1:
        update_result = await db[LIBRARIES].update_one({"_id": ObjectId(object_id)}, {"$set": library})
        if update_result.modified_count == 1:
            if (updated_library := await db_find_library(object_id)) is not None:
                return updated_library

    # No modification to do or update failed
    if (library := await db_find_library(object_id)) is not None:
        return library

    raise HTTPException(status_code=404, detail=f"Library {object_id} not found")


async def db_delete_library(object_id: str):
    return await db[LIBRARIES].delete_one({"_id": ObjectId(object_id)})
