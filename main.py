import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from agent.graph import graph
from agent.memory_state import InitialState
from core.logger_format import logger
from core.timing import TrackInference
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    print("ArchiveNode Tables Initialized")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"message": "Running healthy"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"message": "Everything ready!"}


@app.get("/health/Agents")
async def health_agents() -> dict[str, str]:
    return {"message": "All agents are running correcty"}


@app.get("/metrics")
async def metrics() -> dict[str, str]:
    return {"message": "Future metrics of the system"}


@app.get("/version")
async def version() -> dict[str, str]:
    return {"message": "Current version of the code"}


@app.post("/scout")
async def run_scout(payload: InitialState, thread_id: str | None = None) -> dict[str, Any]:
    effective_thread_id = thread_id or str(uuid4())
    config = {"configurable": {"thread_id": effective_thread_id}}

    with TrackInference() as timer:
        result = await graph.ainvoke(payload.model_dump(), config=config)

    agent_response = result.get("final_report") or "No relevant insights retrieved from memory."

    return {
        "agent_response": agent_response,
        "thread_id": effective_thread_id,
        "latency_breakdown": {"ai_inference_sec": round(timer.duration, 4)},
    }


@app.middleware("http")
async def log_latency(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(f"Request: {request.method} {request.url.path}", extra={"latency": process_time})
    return response
