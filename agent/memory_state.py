import operator
from typing import Annotated, List, Optional, TypedDict

from pydantic import BaseModel, Field


class ScoutFinding(BaseModel):
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"
    relevance_score: float = 0.0


class AgentState(TypedDict):
    query: str
    findings: Annotated[List[ScoutFinding], operator.add]
    critic_feedback: Optional[str]
    iteration: int
    final_report: Optional[str]


class GraphConfig(BaseModel):
    thread_id: str = Field(..., description="Unique identifier for the persistence layer")


class InitialState(BaseModel):
    query: str
    findings: List[ScoutFinding] = Field(default_factory=list)
    iteration: int = 0
    critic_feedback: Optional[str] = None
    final_report: Optional[str] = None


class ResearchResponse(BaseModel):
    """Structured list of findings from the web search."""

    findings: List[ScoutFinding]
