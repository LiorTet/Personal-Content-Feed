import os
from typing import Any, List, Optional

import dotenv
from asyncddgs import aDDGS
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

from agent.memory_state import AgentState, ScoutFinding

dotenv.load_dotenv()


class InitialState(BaseModel):
    query: str
    findings: List[ScoutFinding] = Field(default_factory=list)
    iteration: int = 0
    critic_feedback: Optional[str] = None
    final_report: Optional[str] = None


class ResearchResponse(BaseModel):
    """Structured list of findings from the web search."""

    findings: List[ScoutFinding]


model = MistralModel(
    "mistral-small-latest",
    provider=MistralProvider(api_key=os.getenv("MISTRAL_API_KEY")),
)

scout_agent = Agent(
    model,
    output_type=ResearchResponse,
    system_prompt=(
        "You are a high-fidelity Research Scout. "
        "When reporting findings, the 'source' field must be the NAME OF THE WEBSITE "
        "(e.g., 'ABC.es', 'El País', 'La Linterna Azul'), NOT the search engine name. "
        "Extract the source name from the URL or the search snippet. "
        "Trust the specific dates found in the snippets for 2025 and 2026."
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


async def scout_node(state: AgentState) -> dict[str, Any]:
    current_query = state["query"]
    if state.get("critic_feedback"):
        current_query += f"\n\nAdditional Instruction from Critic: {state['critic_feedback']}"

    result = await scout_agent.run(current_query)

    new_findings = result.output.findings

    return {
        "findings": new_findings,
        "iteration": state["iteration"] + 1,
    }
