from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from agent.nodes.scout import scout_agent
from main import app


@pytest.mark.asyncio
async def test_scout_endpoint_schema() -> None:
    async def scout_model_logic(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        if messages and any(isinstance(p, ToolReturnPart) for p in messages[-1].parts):
            mock_json_response = (
                '{"findings": '
                '[{"title": "Prada News", "url": "http://x.com", "snippet": "Mocked snippet", "source": "News"}]}'
            )
            return ModelResponse(parts=[TextPart(content=mock_json_response)])

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

    mock_search_results = [
        {"title": "Result 1", "href": "http://example.com/1", "body": "Content 1"},
        {"title": "Result 2", "href": "http://example.com/2", "body": "Content 2"},
    ]

    mock_vectors = [[0.1, 0.2, 0.3]]

    with (
        patch("db.database.async_session"),
        patch("db.database.init_db", new_callable=AsyncMock),
        patch("agent.nodes.scout.aDDGS.text", new_callable=AsyncMock, return_value=mock_search_results),
        patch("agent.nodes.archive.get_embeddings_batch", new_callable=AsyncMock, return_value=mock_vectors),
        patch("agent.nodes.retrieval.get_embeddings_batch", new_callable=AsyncMock, return_value=mock_vectors),
        patch("agent.nodes.archive.async_session") as mock_archive_db,
        patch("agent.nodes.retrieval.async_session") as mock_retrieval_db,
    ):
        mock_session = mock_retrieval_db.return_value.__aenter__.return_value

        mock_db_result = MagicMock()
        mock_session.execute.return_value = mock_db_result

        mock_db_result.scalars.return_value.all.return_value = [
            MagicMock(
                title="Historical Insight 1", url="http://example.com/1", source="Archive", snippet="Mock context 1"
            ),
            MagicMock(
                title="Historical Insight 2", url="http://example.com/2", source="Archive", snippet="Mock context 2"
            ),
        ]

        mock_archive_session = mock_archive_db.return_value.__aenter__.return_value
        mock_archive_session.execute.return_value = mock_db_result

        with scout_agent.override(model=model):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                # 3. Call the endpoint using POST with a JSON payload
                response = await ac.post(
                    "/scout",
                    json={
                        "query": ["Latest articles and public interventions by Juan Manuel de Prada May 2026"],
                        "findings": [],
                        "iteration": 0,
                    },
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
