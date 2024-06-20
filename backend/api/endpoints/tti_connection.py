import os

from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from apicelery.worker import celery_app
from database.db import get_session
from schemas.help_schemas import ResponseInfo
from schemas.help_schemas import TaskTypeCelery
from schemas.help_schemas import WorkflowTask
from schemas.help_schemas import WorkflowTaskDataMonitoring
from schemas.help_schemas import WorkflowTaskResult
from services import tti_connection_services

router = APIRouter(prefix="/tti_connection")


@router.get("/all-registered-tti-gateways/", response_model=ResponseInfo)
async def all_registered_tti_gateways(db: Session = Depends(get_session)):
    try:
        return ResponseInfo(description=tti_connection_services.get_all_registered_tti_gateways(db))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-registered-tti-application/", response_model=ResponseInfo)
async def all_registered_tti_application(db: Session = Depends(get_session)):
    try:
        return ResponseInfo(description=tti_connection_services.get_all_registered_tti_application(db))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registered-tti-application/{application_id}", response_model=ResponseInfo)
async def get_registered_tti_application(
        *, application_id: str, db: Session = Depends(get_session)
):
    try:
        return ResponseInfo(description=tti_connection_services.registered_tti_application(db, application_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-registered-tti-gateways-celery/", response_model=WorkflowTask)
async def all_registered_tti_gateways():
    try:
        workflow_task_data = WorkflowTaskDataMonitoring()
        workflow_task_data.task_type = TaskTypeCelery.Monitoring
        workflow_task_data.func_name = "get_all_registered_tti_gateways"
        queue_name = os.getenv("ASYNCQUEUE_NAME", "async_queue")
        result = celery_app.send_task(
            "process_workflow", args=[workflow_task_data.json(), queue_name]
        )

        return {"task_id": str(result.id), "task_status": "Processing"}

    except Exception as e:
        tti_connection_services.logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registered-all-tti-application-celery/", response_model=WorkflowTask)
async def all_registered_tti_application():
    try:
        workflow_task_data = WorkflowTaskDataMonitoring()
        workflow_task_data.task_type = TaskTypeCelery.Monitoring
        workflow_task_data.func_name = "get_all_registered_tti_application"
        queue_name = os.getenv("ASYNCQUEUE_NAME", "async_queue")
        result = celery_app.send_task(
            "process_workflow", args=[workflow_task_data.json(), queue_name]
        )

        return {"task_id": str(result.id), "task_status": "Processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{task_id}",
    response_model=WorkflowTaskResult,
    status_code=202,
    responses={202: {"model": WorkflowTask, "description": "Accepted: Not Ready"}},
)
async def task_status(task_id):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(
            status_code=202, content={"task_id": str(task_id), "task_status": "Processing"}
        )
    result = task.get()
    return {"task_id": task_id, "task_status": "Success", "outcome": str(result)}
