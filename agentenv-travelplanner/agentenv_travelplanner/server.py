"""
TravelPlanner FastAPI Server
"""

import logging
import time
from typing import List, Dict, Any

from fastapi import FastAPI, Request, HTTPException

from .environment import travelplanner_env_server
from .model import *

app = FastAPI(title="TravelPlanner Environment", debug=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


# 自定义中间件记录请求响应时间
@app.middleware("http")
async def log_request_response_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {process_time:.2f} seconds"
    )
    return response


@app.get("/", response_model=str)
async def hello():
    """测试连接"""
    return "This is TravelPlanner Environment for AgentGym"


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "TravelPlanner Environment"}


@app.get("/list_envs", response_model=List[int])
async def list_environments():
    """列出所有环境实例"""
    try:
        envs = travelplanner_env_server.list_environments()
        logger.info(f"Listed {len(envs)} environments")
        return envs
    except Exception as e:
        logger.error(f"Failed to list environments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create", response_model=CreateResponse)
async def create():
    """创建新的环境实例"""
    try:
        env_id = travelplanner_env_server.create()
        logger.info(f"Created environment with ID: {env_id}")
        return CreateResponse(id=env_id)
    except Exception as e:
        logger.error(f"Failed to create environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset", response_model=ResetResponse)
async def reset(reset_query: ResetQuery):
    """重置环境"""
    try:
        logger.info(f"Resetting environment {reset_query.env_idx} with query_id {reset_query.query_id}")
        state, info = travelplanner_env_server.reset(reset_query.env_idx, reset_query.query_id)
        
        return ResetResponse(state=state, info=info)
    except ValueError as e:
        logger.error(f"Invalid environment ID: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to reset environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step", response_model=StepResponse)
async def step(step_query: StepQuery):
    """执行环境步骤"""
    try:
        logger.info(f"Step in environment {step_query.env_idx}: {step_query.action[:100]}...")
        state, reward, done, info = travelplanner_env_server.step(step_query.env_idx, step_query.action)
        
        return StepResponse(state=state, reward=reward, done=done, info=info)
    except ValueError as e:
        logger.error(f"Invalid environment or action: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info", response_model=InfoResponse)
async def get_info(env_idx: int):
    """获取环境信息"""
    try:
        logger.info(f"Getting info for environment {env_idx}")
        info = travelplanner_env_server.get_info(env_idx)
        return InfoResponse(info=info)
    except ValueError as e:
        logger.error(f"Invalid environment ID: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get environment info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observation", response_model=ObservationResponse)
async def get_observation(env_idx: int):
    """获取当前观察"""
    try:
        logger.info(f"Getting observation for environment {env_idx}")
        info = travelplanner_env_server.get_info(env_idx)
        env = travelplanner_env_server.environments[env_idx]
        
        # 构建当前观察
        observation = f"Step {env.step_count}/{env.max_steps}\n"
        observation += f"Current Query: {env.current_query['query']}\n\n"
        
        if env.notebook_content:
            observation += "Notebook Contents:\n"
            for note in env.notebook_content[-5:]:  # 显示最近5条笔记
                observation += f"- {note['content']}\n"
            observation += "\n"
        
        observation += f"Available Tools: {', '.join(env.available_tools)}\n"
        
        return ObservationResponse(observation=observation)
    except ValueError as e:
        logger.error(f"Invalid environment ID: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get observation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return {"error": "Internal server error", "details": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 