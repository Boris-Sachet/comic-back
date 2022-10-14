from os.path import isfile

from fastapi import APIRouter, HTTPException
from websockets.exceptions import ConnectionClosedOK

from starlette.websockets import WebSocket

from app.services.db_service import find_file
from app.services.file_service import execute_action, get_current_page, get_full_path

router = APIRouter(prefix="/file", tags=["File"], responses={404: {"file": "Not found"}})


# @router.get("/", response_class=FileResponse)
# async def get_file(path: str):
#     file_path = join(base_dir, path)
#     if isfile(file_path):
#         return FileResponse(file_path)


@router.websocket("/")
async def stream_file(websocket: WebSocket, file_id: str):
    """Open a new websocket on a file streaming one page at  the time, to control it use:
        + : next page
        - : previous page
        any number : jump top page number (if exist)"""
    resume_token = None  # TODO Manage resume on error
    try:
        await websocket.accept()
        file = await find_file(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found in database")

        if not isfile(get_full_path(file.full_path)):
            raise HTTPException(status_code=404, detail="File not found on storage")

        # Send current page then await command, execute command then send current page
        await websocket.send_bytes(get_current_page(file))
        while True:
            action = await websocket.receive_text()
            file = await execute_action(file, action)
            await websocket.send_json(file.json())
            await websocket.send_bytes(get_current_page(file))

    except ConnectionClosedOK:
        pass
    except Exception as e:
        print(e)
