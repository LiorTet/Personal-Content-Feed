import asyncio
from typing import Any

from sqlmodel import select

from agent.memory_state import AgentState
from agent.nodes.archive import ContentArchive, get_embeddings_batch
from db.database import async_session


async def retrieval_node(state: AgentState) -> dict[str, Any]:
    query = state["query"]

    if not query:
        return {"final_report": "No information for retrieval."}

    await asyncio.sleep(0.5)

    try:
        vectors = await get_embeddings_batch([query])
        query_vector = vectors[0]
    except Exception as e:
        print(f"Mistral Retrieval Embedding Error: {e}")
        return {"final_report": f"Failed to retrieve context due to embedding error: {e}"}

    async with async_session() as session:
        stmt = select(ContentArchive).order_by(ContentArchive.embedding.l2_distance(query_vector)).limit(3)
        result = await session.execute(stmt)
        records = result.scalars().all()

    if not records:
        return {"final_report": f"No historical matches found for query: '{query}'"}

    report_lines = [f"## Semantic Memory Insights for: '{query}'\n"]
    for idx, record in enumerate(records, 1):
        report_lines.append(f"{idx}. **[{record.title}]({record.url})** (Source: {record.source})")
        report_lines.append(f"   > {record.snippet}\n")

    return {"final_report": "\n".join(report_lines)}
