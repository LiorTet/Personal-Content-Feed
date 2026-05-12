import time
from typing import Any, Awaitable, Callable

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from agent.scout import scout_agent
from core.logger_format import logger
from core.timing import TrackInference

app = FastAPI()


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


@app.get("/scout")
async def run_scout(query: str) -> dict[str, Any]:
    with TrackInference() as timer:
        result = await scout_agent.run(query, model_settings={"tool_choice": "search_web"})

    return {
        "agent_response": result.output,
        "latency_breakdown": {"ai_inference_sec": round(timer.duration, 4)},
    }


@app.middleware("http")
async def log_latency(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(f"Request: {request.method} {request.url.path}", extra={"latency": process_time})
    return response
