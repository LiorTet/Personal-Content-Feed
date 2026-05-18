import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.memory_state import AgentState

from .nodes import archive_node, exporter_node, retrieval_node, scout_node

os.environ["LANGGRAPH_STRICT_MSGPACK"] = "false"


builder = StateGraph(AgentState)

builder.add_node("scout_worker", scout_node)
builder.add_node("archive_worker", archive_node)
builder.add_node("retrieval_worker", retrieval_node)
builder.add_node("exporter_worker", exporter_node)

builder.add_edge(START, "scout_worker")
builder.add_edge("scout_worker", "archive_worker")
builder.add_edge("archive_worker", "retrieval_worker")
builder.add_edge("retrieval_worker", "exporter_worker")
builder.add_edge("exporter_worker", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
