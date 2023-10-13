from fastapi.routing import APIRouter

from content_discovery.web.api import docs, dummy, echo, feed

api_router = APIRouter()
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
