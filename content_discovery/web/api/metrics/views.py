import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends

from content_discovery.db.dao.snaps_dao import SnapDAO

router = APIRouter()

START_YEAR = 1970
START_DATE = datetime.datetime(START_YEAR, 1, 1, 1, 1, 1)


@router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """


@router.get("/get_snap_rates", response_model=None)
async def snap_rates(snaps_dao: SnapDAO = Depends()) -> Dict[str, str]:
    """Get snap rates for public and private snaps."""
    snapcounts = await snaps_dao.quantity_new_snaps_in_time_period(
        start=START_DATE,
        end=datetime.datetime.now(),
    )
    snapcounts_public = await snaps_dao.quantity_new_snaps_in_time_period(
        start=START_DATE,
        end=datetime.datetime.now(),
        filter_only_public=True,
    )
    return {
        "total_snaps": str(snapcounts),
        "private_snaps": str(snapcounts - snapcounts_public),
        "public_snaps": str(snapcounts_public),
    }


@router.get(
    "/{user_id}/get_user_metrics_between_{start_date}_and_{end_date}",
    response_model=None,
)
async def get_user_metrics(
    user_id: str,
    start_date: str,
    end_date: str,
    snaps_dao: SnapDAO = Depends(),
) -> Any:
    """Returns metrics for a user in a time period."""
    return await snaps_dao.get_snap_metrics_by_user(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
