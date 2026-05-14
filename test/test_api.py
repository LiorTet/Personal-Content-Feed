import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from agent.scout import scout_agent
from main import app


@pytest.mark.asyncio
async def test_scout_endpoint_schema() -> None:
    async def scout_model_logic(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        if messages and any(isinstance(p, ToolReturnPart) for p in messages[-1].parts):
            return ModelResponse(parts=[TextPart(content="Mocked search results for Juan Manuel de Prada May 2026")])

        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="search_web",
                    args={
                        "keywords": "Latest articles and public interventions by Juan Manuel de Prada May 2026",
                        "region": "wt-wt",
                        "max_results": 10,
                    },
                )
            ]
        )

    model = FunctionModel(scout_model_logic)

    with scout_agent.override(model=model):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 3. Call the endpoint
            response = await ac.get(
                "/scout", params={"query": "Latest articles and public interventions by Juan Manuel de Prada May 2026"}
            )

            # 4. Assertions
            assert response.status_code == 200
            data = response.json()

            assert "agent_response" in data
            assert isinstance(data["agent_response"], str)

            # Check Graph Metadata
            assert "thread_id" in data
            assert isinstance(data["thread_id"], str)

            # Check Performance Metadata
            assert "latency_breakdown" in data
            assert "ai_inference_sec" in data["latency_breakdown"]
            assert data["latency_breakdown"]["ai_inference_sec"] >= 0
