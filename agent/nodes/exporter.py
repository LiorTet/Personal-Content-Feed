import os
import re
from datetime import datetime
from typing import Any, Dict

from agent.memory_state import AgentState


def slugify(text: str) -> str:
    """Converts a query string into a safe file name."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "_", text).strip("_")


async def exporter_node(state: AgentState) -> Dict[str, Any]:
    report_text = state.get("final_report")
    query_text = state.get("query", "content_feed")

    if not report_text or report_text.startswith("No query") or report_text.startswith("No historical"):
        return {}

    output_dir = "/feeds"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = slugify(query_text)
    filename = f"{timestamp}_{safe_query}.md"
    file_path = os.path.join(output_dir, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Content feed file created successfully: {file_path}")
    except Exception as e:
        print(f"Error writing feed file: {e}")

    return {}
