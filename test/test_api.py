import json

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.models.test import TestModel

from agent.scout import scout_agent
from main import app


@pytest.mark.asyncio
async def test_scout_endpoint_schema() -> None:
    mock_data = {
        "findings": ["Test finding 1", "Test finding 2"],
        "scout_summary": "This is a successful mock summary.",
    }

    with scout_agent.override(model=TestModel(custom_output_text=json.dumps(mock_data))):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 3. Call the endpoint
            response = await ac.get("/scout", params={"query": "Test query"})

            # 4. Assertions
            assert response.status_code == 200
            data = response.json()

            # Verify the top-level contract keys exist
            assert "agent_response" in data
            assert "latency_breakdown" in data
            assert "ai_inference_sec" in data["latency_breakdown"]

            # Verify the agent_response follows our expected structure
            agent_out = data["agent_response"]
            assert isinstance(agent_out["findings"], list)
            assert len(agent_out["findings"]) > 0
            assert "scout_summary" in agent_out
            assert agent_out["scout_summary"] == "This is a successful mock summary."
