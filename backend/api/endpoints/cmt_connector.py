from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlmodel import Session

from database.db import get_session
from schemas.help_schemas import ResponseInfo
from services import cmt_connector_services

router = APIRouter(prefix="/cmt_connector")


@router.get("/update_data_architecture_from_cmt/", response_model=ResponseInfo)
async def update_data_architecture_from_cmt(
    x_authorization_cmt: str, x_authorization_tb: str, db: Session = Depends(get_session)
):
    """
    This route updates data architecture from CMT to TB.

    Args:
        db: the database session
        x_authorization_cmt: the CMT authorization token
        x_authorization_tb: the TB authorization token
    Returns:
        A CmtConnectorInfo object with a 'TASK_COMPLETED' description
    """
    try:
        cmt_connector_services.update_data_architecture_from_cmt(
            db, cmt_auth=x_authorization_cmt, tb_auth=x_authorization_tb
        )
        return ResponseInfo(description="TASK_COMPLETED")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
