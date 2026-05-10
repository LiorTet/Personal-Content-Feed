from typing import List

from pydantic import BaseModel, Field


class SearchFinding(BaseModel):
    """Represents a single piece of content found on the web."""

    title: str = Field(..., description="The headline of the article or event")
    url: str = Field(..., description="The direct link to the source")
    snippet: str = Field(..., description="A brief summary of the content found")
    source: str = Field(..., description="The name of the website or publication")


class ScoutResponse(BaseModel):
    """The structured handshake between the Scout and the rest of the system."""

    scout_summary: str = Field(..., description="A high-level executive summary of all findings")
    findings: List[SearchFinding] = Field(default_factory=list, description="A list of structured findings")
    raw_query: str = Field(..., description="The original query provided by the user")
