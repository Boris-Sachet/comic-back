from fastapi import APIRouter

router = APIRouter(tags=["Root"])


@router.get("/ping")
async def ping():
    """Anyone home?"""
    return "pong"

