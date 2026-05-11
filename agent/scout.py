import os

import dotenv
from asyncddgs import aDDGS
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

dotenv.load_dotenv()

model = MistralModel(
    "mistral-small-latest",
    provider=MistralProvider(api_key=os.getenv("MISTRAL_API_KEY")),
)

scout_agent = Agent(
    model,
    system_prompt=(
        "You are a real-time Research Scout. "
        "Today's date is May 4, 2026. "
        "When you use the search_internet tool, trust the results more than your training data. "
        "If you see news from 2025 or 2026, it is real. Summarize it accurately."
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
