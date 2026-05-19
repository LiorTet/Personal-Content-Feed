import os
from datetime import datetime, timezone
from typing import Any, List, Optional, cast

from mistralai.client import Mistral
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Column, DateTime, Field, SQLModel

from agent.memory_state import AgentState
from db.database import async_session


class ContentArchive(SQLModel, table=True):  # type: ignore
    __tablename__ = "content_archive"

    id: Optional[int] = Field(default=None, primary_key=True)
    query_context: str = Field(index=True)
    title: str
    url: str = Field(unique=True, index=True)
    snippet: str
    source: str
    embedding: Any = Field(sa_column=Column(Vector(1024)))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))


async def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    async with Mistral(api_key=os.getenv("MISTRAL_API_KEY")) as client:
        res = await client.embeddings.create_async(model="mistral-embed", inputs=texts)
        # Extract the list of vectors
        return [cast(List[float], d.embedding) for d in res.data]


async def archive_node(state: AgentState) -> dict[str, Any]:
    if not state.get("findings"):
        return {}

    # Collect all snippets first
    snippets = [f.snippet for f in state["findings"]]
    # Get all embeddings in ONE API call
    try:
        vectors = await get_embeddings_batch(snippets)
    except Exception as e:
        print(f"Mistral Batch Error: {e}")
        return {}

    async with async_session() as session:
        # Zip findings and vectors together to loop through them
        for finding, vector in zip(state["findings"], vectors):
            stmt = (
                insert(ContentArchive)
                .values(
                    query_context=state["query"],
                    title=finding.title,
                    url=finding.url,
                    snippet=finding.snippet,
                    source=finding.source,
                    embedding=vector,
                )
                .on_conflict_do_nothing(index_elements=["url"])
            )
            await session.execute(stmt)

        await session.commit()

    return {"iteration": state["iteration"]}
