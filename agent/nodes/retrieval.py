from datetime import datetime
from typing import Any

from sqlmodel import select

from agent.memory_state import AgentState
from agent.nodes.archive import ContentArchive, get_embeddings_batch
from db.database import async_session


async def retrieval_node(state: AgentState) -> dict[str, Any]:
    queries = state["query"]  # This is now List[str]

    if not queries:
        return {"final_report": "No information for retrieval."}

    try:
        query_vectors = await get_embeddings_batch(queries)
    except Exception as e:
        return {"final_report": f"Failed to retrieve context due to embedding error: {e}"}

    report_lines = [
        "# 🔍 Research Synthesis Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---",
    ]

    async with async_session() as session:
        # Loop through each topic and its corresponding vector
        for q, q_vec in zip(queries, query_vectors):
            stmt = select(ContentArchive).order_by(ContentArchive.embedding.l2_distance(q_vec)).limit(3)
            result = await session.execute(stmt)
            records = result.scalars().all()

            report_lines.append(f"### 🎯 Topic: {q}")
            if not records:
                report_lines.append("> *No semantic matches found in current memory store for this topic.*")
            else:
                # Using a table-like layout for visual clarity
                report_lines.append("| Title | Source |")
                report_lines.append("| :--- | :--- |")
                for record in records:
                    report_lines.append(f"| [{record.title}]({record.url}) | {record.source} |")
                report_lines.append(f"\n> **Snippet Summary:** {records[0].snippet[:150]}...")
            report_lines.append("\n---\n")

    return {"final_report": "\n".join(report_lines)}
