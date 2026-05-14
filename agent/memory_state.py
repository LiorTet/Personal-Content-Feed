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
