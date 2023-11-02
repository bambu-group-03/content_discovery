from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.models.snaps_model import SnapsModel

router = APIRouter()


@router.get("/{hashtag}", response_model=None)
async def filter_hashtags(
    hashtag: str,
    hashtag_dao: HashtagDAO = Depends(),
) -> List[SnapsModel]:
    """Retrieve a list of filtered snaps by hashtags."""
    return await hashtag_dao.filter_hashtags(hashtag)
