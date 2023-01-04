from os.path import isfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, FileResponse
from websockets.exceptions import ConnectionClosedOK

from fastapi.websockets import WebSocket

from app.model.file_model import ResponseFileModel, FileModel
from app.services.db_service import db_find_file, db_find_library_by_name
from app.services.directory_service import DirectoryService
from app.services.file_service import FileService

router = APIRouter(prefix="/file", tags=["File"], responses={404: {"file": "Not found"}})


async def get_library_file(library_name: str, file_id: str):
    """Get the library and file objects in database based on their identifiers or return the proper error"""
    library = await db_find_library_by_name(library_name)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found in database")

    file = await db_find_file(library_name, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found in database")

    if not isfile(FileService.get_full_path(library, file.full_path)):
        raise HTTPException(status_code=404, detail="File not found on storage")

    return library, file


def format_file_response(file: FileModel, image_bytes: bytes):
    image_format = file.pages_names[0].split('.')[-1]
    headers = {"Content-Disposition": f"inline; filename=\"{file.id}-0.{image_format}\""}
    return Response(content=image_bytes, media_type=f"image/{image_format}", headers=headers)


@router.get("/{library_name}/{file_id}/cover", response_class=Response)
async def get_cover(library_name: str, file_id: str) -> FileResponse:
    """Get the cover/first page of a file"""
    library, file = await get_library_file(library_name, file_id)
    if DirectoryService.thumbnail_exist(library, file):
        return FileResponse(DirectoryService.get_thumbnail_path(library, file))
    raise HTTPException(status_code=404, detail="No cover for this file")


@router.get("/{library_name}/{file_id}/page/{page_number}", response_class=Response)
async def get_page(library_name: str, file_id: str, page_number: int):
    """Get page of a file"""
    library, file = await get_library_file(library_name, file_id)
    if page_number not in range(0, file.pages_count):
        raise HTTPException(status_code=404, detail="Page not found in file")
    return format_file_response(file, FileService.get_page(library, file, page_number))


@router.get("/{library_name}/{file_id}/page/{page_number}", response_class=Response)
async def read_page(library_name: str, file_id: str, page_number: int):
    """Get page of a file and set it as the current page for the file"""
    library, file = await get_library_file(library_name, file_id)
    if page_number not in range(0, file.pages_count):
        raise HTTPException(status_code=404, detail="Page not found in file")
    file = await FileService.set_page(library, file, page_number)
    return format_file_response(file, FileService.get_current_page(library, file))


@router.get("/{library_name}/{file_id}/page/next", response_class=Response)
async def read_next(library_name: str, file_id: str):
    """Get the next page of a file and set it as the current page for the file"""
    library, file = await get_library_file(library_name, file_id)
    file = await FileService.next_page(library, file)
    return format_file_response(file, FileService.get_current_page(library, file))


@router.get("/{library_name}/{file_id}/page/prev", response_class=Response)
async def read_previous(library_name: str, file_id: str):
    """Get the previous page of a file and set it as the current page for the file"""
    library, file = await get_library_file(library_name, file_id)
    file = await FileService.next_page(library, file)
    return format_file_response(file, FileService.get_current_page(library, file))


@router.websocket("/")
async def stream_file(websocket: WebSocket, library_name: str, file_id: str):
    """Open a new websocket on a file streaming one page at  the time, to control it use:
        + : next page
        - : previous page
        any number : jump top page number (if exist)"""
    resume_token = None  # TODO Manage resume on error
    try:
        await websocket.accept()
        library, file = get_library_file(library_name, file_id)

        # Send current page then await command, execute command then send current page
        await websocket.send_json(ResponseFileModel(**file.dict()).json())
        await websocket.send_bytes(FileService.get_current_page(library, file))
        while True:
            action = await websocket.receive_text()
            file = await FileService.execute_action(library, file, action)
            await websocket.send_json(ResponseFileModel(**file.dict()).json())
            await websocket.send_bytes(FileService.get_current_page(library, file))

    except ConnectionClosedOK:
        pass
    except Exception as e:
        print(e)
