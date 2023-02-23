import logging
from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from app.endpoint.base_models.custom_response_models import LibContentResponseModel, LibraryResponseModel

from app.model.library_model import UpdateLibraryModel, LibraryModel
from app.services.db_service import db_find_all_libraries, db_find_library_by_name, db_insert_library, \
    db_delete_library, db_update_library, db_remove_collection
from app.services.directory_service import DirectoryService
from app.services.file_service import FileService
from app.services.library_service import create_library_model

router = APIRouter(prefix="/library", tags=["Library"], responses={404: {"library": "Not found"}})
LOGGER = logging.getLogger(__name__)



@router.get("/", response_model=List[LibraryResponseModel])
async def get_libraries():
    """Get a list of all libraries"""
    return await db_find_all_libraries()


@router.get("/{name}", response_model=LibraryResponseModel)
async def get_library(name: str):
    return await db_find_library_by_name(name)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_library(name: str, path: str, hidden: bool, connect_type: str, user: str | None, password: str | None):
    library_search = await db_find_library_by_name(name)
    if library_search is not None:
        raise HTTPException(status_code=409, detail=f"Library {name} already exist")

    creation_result = await db_insert_library(create_library_model(
        name=name, path=path, hidden=hidden, connect_type=connect_type, user=user, passsword=password))
    if not creation_result.inserted_id:
        raise HTTPException(status_code=400, detail="Impossible to insert new library")


@router.put("/{name}", response_model=LibraryResponseModel)
async def update_library(name: str, library: UpdateLibraryModel):
    library_from_db = await db_find_library_by_name(name)

    if library_from_db is not None:
        return await db_update_library(str(library_from_db.id), library)

    raise HTTPException(status_code=404, detail=f"Library {name} not found")


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_library(name: str):
    library_from_db = await db_find_library_by_name(name)

    if library_from_db is not None:
        await db_delete_library(str(library_from_db.id))
        await db_remove_collection(name)
    else:
        raise HTTPException(status_code=404, detail=f"Library {name} not found")


@router.get("/{library_name}/content", response_model=LibContentResponseModel)
async def get_path_content(library_name: str, path: str = ""):
    library = await db_find_library_by_name(library_name)
    # Remove leading slash or backslash
    if path.startswith("\\") or path.startswith("/"):
        path = path.lstrip(path[0])
    try:
        result = await DirectoryService.get_dir_content(library, path, True)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Folder {path} not found")
    return result


@router.get("/{library_name}/scan")
async def scan_base_directory(library_name: str, purge: bool = False):
    library = await db_find_library_by_name(library_name)
    LOGGER.info(f"Starting library {library_name} scan")
    await DirectoryService.scan_in_depth(library, "")
    LOGGER.info(f"Scan completed for library {library_name} scan")
    if purge:
        await FileService.purge_deleted_files(library)
