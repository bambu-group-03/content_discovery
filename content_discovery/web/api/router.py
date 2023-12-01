from fastapi.routing import APIRouter

from content_discovery.web.api import docs, feed, filter, interactions

api_router = APIRouter()
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(
    interactions.router,
    prefix="/interactions",
    tags=["interactions"],
)
api_router.include_router(docs.router)
api_router.include_router(filter.router, prefix="/filter", tags=["filter"])
