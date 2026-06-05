import os
from typing import Any

import dotenv
from asyncddgs import aDDGS
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

from agent.memory_state import ResearchResponse, WorkerState

dotenv.load_dotenv()


model = MistralModel(
    "mistral-small-latest",
    provider=MistralProvider(api_key=os.getenv("MISTRAL_API_KEY")),
)

scout_agent = Agent(
    model,
    output_type=ResearchResponse,
    system_prompt=(
        "You are a specialized Research Scout for public intellectuals. "
        "Your task is to find specific, factual information for the query provided. "
        "If a specific name is provided (e.g., Gabriel Albiac), you MUST prioritize "
        "content specifically about that person. Do not return generic 'no results found' "
        "for one topic just because the other returned nothing. Be exhaustive."
    ),
)


@scout_agent.tool_plain  # type: ignore[misc]
async def search_web(keywords: str, region: str = "wt-wt", max_results: int = 10) -> str:
    """
    Search the internet for real-time information.
    - keywords: Specific search terms.
    - region: The country/language code (e.g., 'es-es' for Spain, 'us-en' for USA).
    - max_results: Number of results to return.
    """
    async with aDDGS() as addgs:
        results = await addgs.text(
            keywords=keywords,
            region=region,
            safesearch="moderate",
            timelimit="m",
            max_results=max_results,
        )

        output = []
        for r in results:
            output.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}")

        return "\n\n".join(output) if output else "No results found."


async def scout_node(state: WorkerState) -> dict[str, Any]:
    current_query = state["query"]
    if state.get("critic_feedback"):
        current_query += f"\n\nAdditional Instruction from Critic: {state['critic_feedback']}"

    result = await scout_agent.run(current_query)
    new_findings = result.output.findings

    for finding in new_findings:
        finding.origin_query = state["query"]

    return {"findings": new_findings}
