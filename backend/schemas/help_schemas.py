from enum import Enum
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class BaseModelConfig(BaseModel):
    """
    Base configuration class for Pydantic models.
    """

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class DecodedJWT(BaseModelConfig):
    """
    Pydantic model for a decoded JSON Web Token (JWT).
    """

    sub: str
    user_id: UUID = Field(..., alias="userId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    tenant_id: UUID = Field(..., alias="tenantId")
    scopes: List[str]
    iat: int
    exp: int


class TaskType(str, Enum):
    """
    Enumeration for task types.
    """

    TRAINING = "training"
    SERVING = "serving"
    MONITORING = "stream_event_logger"


class ControlCommands(str, Enum):
    """
    Enumeration for control commands.
    """

    START = "start"
    STOP = "stop"


class MonitorInfo(BaseModel):
    """
    Pydantic model for monitor information.
    """

    id: str
    command: ControlCommands = ControlCommands.START


class MonitorInfoList(BaseModel):
    """
    Pydantic model for monitor information.
    """

    ids: List[str]
    command: ControlCommands = ControlCommands.START


class MonitorCont(BaseModel):
    """
    Pydantic model for monitor information.
    """

    command: ControlCommands = ControlCommands.START


class WorkflowTaskResult(BaseModel):
    """
    Pydantic model for a workflow task result.
    """

    task_id: str
    task_status: str
    outcome: str


class MonitoringTaskResult(BaseModel):
    """
    Pydantic model for a workflow task result.
    """

    task_status: str


class ResponseInfo(BaseModel):
    """
    Pydantic model for CMT connector information.
    """

    description: str


class TaskTypeCelery(str, Enum):
    TRAINING = "training"
    SERVING = "serving"
    Monitoring = "metadatalogger"


class WorkflowTaskDataMonitoring(BaseModel):
    task_type: TaskType = TaskTypeCelery.Monitoring
    payload: Optional[str] = None
    func_name: Optional[str] = None
    description: Optional[str] = None


class WorkflowTask(BaseModel):
    task_id: str
    task_status: str


class WorkflowTaskResultCelery(BaseModel):
    task_id: str
    task_status: str
    outcome: str


class WorkflowTaskCancelled(BaseModel):
    task_id: str
    task_status: str
