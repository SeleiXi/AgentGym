from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class CreateResponse(BaseModel):
    """响应创建环境的结果"""
    id: int


class StepQuery(BaseModel):
    """步骤请求的数据模型"""
    env_idx: int
    action: str


class StepResponse(BaseModel):
    """步骤响应的数据模型"""
    state: str
    reward: float
    done: bool
    info: Dict[str, Any]


class ResetQuery(BaseModel):
    """重置请求的数据模型"""
    env_idx: int
    query_id: int


class ResetResponse(BaseModel):
    """重置响应的数据模型"""
    state: str
    info: Dict[str, Any]


class ObservationResponse(BaseModel):
    """观察响应的数据模型"""
    observation: str


class InfoResponse(BaseModel):
    """信息响应的数据模型"""
    info: Dict[str, Any] 