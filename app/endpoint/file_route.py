import pathlib
from os.path import isfile, join

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from websockets.exceptions import ConnectionClosedOK

from app.endpoint import base_dir
from app.model.file import File
from starlette.websockets import WebSocket

from app.services.file_service import find_file

router = APIRouter(prefix="/file", tags=["File"], responses={404: {"file": "Not found"}})


@router.get("/{path}", response_class=FileResponse)
async def get_file(path: str):
    file_path = join(base_dir, path)
    if isfile(file_path):
        return FileResponse(file_path)


@router.websocket("/{path}")
async def stream_file(websocket: WebSocket, path: str):
    resume_token = None
    try:
        await websocket.accept()
        #Send first data then begin watch
        file = find_file(path)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Stream the file page by page via the websocket
        # for image in file.iterfile():
        for image in file:
            await websocket.send_bytes(image)

    except ConnectionClosedOK:
        pass
    except Exception as e:
        print(e)