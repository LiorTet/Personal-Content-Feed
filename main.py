from fastapi import FastAPI

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
