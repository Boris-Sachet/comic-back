import logging
import re
from datetime import datetime, timedelta
from typing import List

import pymongo
from bson import ObjectId
from fastapi import HTTPException

from app.database_connect import db
from app.model.file_model import FileModel, UpdateFileModel
from app.model.library_model import LibraryModel, UpdateLibraryModel

LOGGER = logging.getLogger(__name__)


# ===========================
# COLLECTION SPECIFIC METHODS
# ===========================
async def db_remove_collection(collection_name: str):
    """Delete a database collection"""
    LOGGER.info(f"Dropping collection: {collection_name}")
    return await db[collection_name].drop()


# =====================
# FILE SPECIFIC METHODS
# =====================
async def db_find_file(library_name: str, object_id: str) -> FileModel | None:
    """Find a file in a library by id"""
    file_dict = await db[library_name].find_one({"_id": ObjectId(object_id)})
    if file_dict is not None:
        LOGGER.debug(f"File id '{file_dict['full_path']}' found in database library {library_name}")
        return FileModel(**file_dict)
    LOGGER.error(f"File id '{object_id}' not found in database library {library_name}")
    return None


async def db_find_file_by_full_path(library_name: str, file_path: str) -> FileModel | None:
    """Find a file in a library by full path"""
    file_dict = await db[library_name].find_one({"full_path": file_path})
    if file_dict is not None:
        LOGGER.debug(f"File full path '{file_dict['full_path']}' found in database library {library_name}")
        return FileModel(**file_dict)
    LOGGER.error(f"File full path '{file_path}' not found in database library {library_name}")
    return None


async def db_find_file_by_md5(library_name: str, md5: str) -> FileModel | None:
    """Find a file in a library by md5"""
    file_dict = await db[library_name].find_one({"md5": md5})
    if file_dict is not None:
        LOGGER.debug(f"File md5 '{file_dict['full_path']}' found in database library {library_name}")
        return FileModel(**file_dict)
    LOGGER.error(f"File md5 '{md5}' not found in database library {library_name}")
    return None


async def db_find_all_files(library_name: str) -> List[dict]:
    """Get a list of all files in library"""
    LOGGER.debug(f"Listing all files in library {library_name}")
    return await db[library_name].find().to_list(None)


async def db_find_first_child_in_path(library_name: str, dir_path: str) -> FileModel | None:
    """Find the first file in a directory, or it's sub-dirs"""
    # Search in direct folder children first
    file_dict = await db[library_name].find_one(
        {"path": dir_path}, sort=[('path', pymongo.ASCENDING), ('name', pymongo.ASCENDING)])
    # If not found look in sub-folders
    if file_dict is None:
        dir_path = re.escape(dir_path + "/")
        pattern = re.compile(rf'^{dir_path}.*')
        file_dict = await db[library_name].find_one(
            {"path": {"$regex": pattern}}, sort=[('path', pymongo.ASCENDING), ('name', pymongo.ASCENDING)])
    if file_dict is not None:
        LOGGER.debug(f"First file for path {dir_path} in library {library_name} is {file_dict['full_path']}")
        return FileModel(**file_dict)
    LOGGER.info(f"Path {dir_path} in library {library_name} has no files")
    return None


async def db_find_last_ongoing(library_name: str, limit: int) -> List[FileModel]:
    """Find the last updated files that have current_page > 0 and current_page != pages_count -1."""
    query = {
        "current_page": {"$gt": 0, "$ne": "None"},
        "$expr": {"$lt": ["$current_page", {"$subtract": ["$pages_count", 1]}]}
    }
    cursor = db[library_name].find(query).sort([("update_date", pymongo.DESCENDING)]).limit(limit)
    ongoing_files = []
    async for document in cursor:
        ongoing_files.append(FileModel(**document))
    LOGGER.info(f"Found {len(ongoing_files)} ongoing files in library {library_name}, limited to {limit}")
    return ongoing_files


async def db_find_last_added(library_name: str, limit: int) -> List[FileModel]:
    """Find the last added files in the database."""
    cursor = db[library_name].find({}).sort([("add_date", pymongo.DESCENDING)]).limit(limit)
    latest_files = []
    async for document in cursor:
        latest_files.append(FileModel(**document))
    LOGGER.info(f"Found {len(latest_files)} recently added files in library {library_name}, limited to {limit}")
    return latest_files


async def db_find_last_added_by_days(library_name: str, days: int, limit: int = None) -> List[FileModel]:
    """Find files added in the last `days` days."""
    date_threshold = datetime.now() - timedelta(days=days)
    query = {"add_date": {"$gt": date_threshold}}
    if limit is not None:
        cursor = db[library_name].find(query).sort([("add_date", pymongo.DESCENDING)]).limit(limit)
    else:
        cursor = db[library_name].find(query).sort([("add_date", pymongo.DESCENDING)])
    latest_files = []
    async for document in cursor:
        latest_files.append(FileModel(**document))
    LOGGER.info(f"Found {len(latest_files)} files added in the last {days} in library {library_name}, limited to {limit}")
    return latest_files


async def db_insert_file(library_name: str, file: FileModel):
    """Insert a new file in library"""
    return await db[library_name].insert_one(file.dict(by_alias=True))


async def db_update_file(library_name: str, object_id: str, file: UpdateFileModel) -> FileModel:
    """Update an existing file by his id with an  update model"""
    file = {key: value for key, value in file.dict().items() if value is not None}

    # If there is modifications to do
    if len(file) >= 1:
        update_result = await db[library_name].update_one({"_id": ObjectId(object_id)}, {"$set": file})
        if update_result.modified_count == 1:
            if (updated_file := await db_find_file(library_name, object_id)) is not None:
                return updated_file

    # No modification to do or update failed
    if (file := await db_find_file(library_name, object_id)) is not None:
        return file

    raise HTTPException(status_code=404, detail=f"File {object_id} not found")


async def db_delete_file(library_name: str, object_id: str):
    """Delete a file data in library"""
    return await db[library_name].delete_one({"_id": ObjectId(object_id)})


# ========================
# LIBRARY SPECIFIC METHODS
# ========================
LIBRARIES = "libraries"


async def db_find_library(object_id: str) -> LibraryModel | None:
    """Find a library by id"""
    library_dict = await db[LIBRARIES].find_one({"_id": ObjectId(object_id)})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_library_by_name(name: str) -> LibraryModel | None:
    """Find a library by name"""
    library_dict = await db[LIBRARIES].find_one({"name": name})
    if library_dict is not None:
        return LibraryModel(**library_dict)
    return None


async def db_find_all_libraries() -> List[LibraryModel]:
    """Get a list of all libraries"""
    return await db[LIBRARIES].find().to_list(None)


async def db_insert_library(library: LibraryModel):
    """Create a new library"""
    return await db[LIBRARIES].insert_one(library.dict(by_alias=True))


async def db_update_library(object_id: str, library: UpdateLibraryModel) -> LibraryModel:
    """Update a library by his id with an update model"""
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
    """Delete a library"""
    return await db[LIBRARIES].delete_one({"_id": ObjectId(object_id)})
