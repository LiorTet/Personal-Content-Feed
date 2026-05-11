import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.models.test import TestModel

from agent.scout import scout_agent
from main import app


@pytest.mark.asyncio  # type: ignore[misc]
async def test_scout_endpoint_schema() -> None:
    # 1. Mock the agent so we don't hit the real LLM in CI
    with scout_agent.override(model=TestModel()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 2. Call the endpoint
            response = await ac.get("/scout", params={"query": "Test query"})

            # 3. Assertions
            assert response.status_code == 200
            data = response.json()

            # Verify the contract keys exist
            assert "agent_response" in data
            assert "latency_breakdown" in data
            assert "ai_inference_sec" in data["latency_breakdown"]

            # Verify the agent_response follows our ScoutResponse schema
            agent_out = data["agent_response"]
            assert isinstance(agent_out["findings"], list)
            assert "scout_summary" in agent_out
