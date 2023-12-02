from fastapi import APIRouter, Depends
from typing import Dict
from content_discovery.db.dao.snaps_dao import SnapDAO
import datetime

router = APIRouter()


@router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """

@router.get("/get_snap_rates",  response_model=None)
async def snap_rates(snaps_dao: SnapDAO = Depends()) -> Dict[str, str]:
    """
    Checks the health of a project.
    It returns 200 if the project is healthy.
    """
    snapcounts = await snaps_dao.quantity_new_snaps_in_time_period(
        start=datetime.datetime(1970,1,1,1,1,1),
        end=datetime.datetime.now()
    )
    return {
        "total_snaps": str(snapcounts),
        "private_snaps": "0",
        "public_snaps": str(snapcounts),
    }
