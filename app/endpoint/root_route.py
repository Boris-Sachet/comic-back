from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["Root"])


@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    """Anyone home?"""
    return 'pong'
