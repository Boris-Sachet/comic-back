from os.path import isfile, join

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from websockets.exceptions import ConnectionClosedOK

from app.endpoint import base_dir
from starlette.websockets import WebSocket

from app.services.file_service import find_file, execute_action

router = APIRouter(prefix="/file", tags=["File"], responses={404: {"file": "Not found"}})


@router.get("/", response_class=FileResponse)
async def get_file(path: str):
    file_path = join(base_dir, path)
    if isfile(file_path):
        return FileResponse(file_path)


@router.websocket("/")
async def stream_file(websocket: WebSocket, path: str):
    """Open a new websocket on a file streaming one page at  the time, to control it use:
        + : next page
        - : previous page
        any number : jump top page number (if exist)"""
    resume_token = None
    try:
        await websocket.accept()
        file = find_file(path)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Send current page then await command, execute command then send current page
        await websocket.send_bytes(file.get_current_page())
        #TODO send a model with the info of the File object as metadata when opening the file, send another one at each actions to indicate the current page number to avoid confusion
        while True:
            action = await websocket.receive_text()
            execute_action(file, action)
            await websocket.send_bytes(file.get_current_page())

    except ConnectionClosedOK:
        pass
    except Exception as e:
        print(e)
