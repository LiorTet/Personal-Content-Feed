import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.memory_state import AgentState
from agent.scout import scout_node

os.environ["LANGGRAPH_STRICT_MSGPACK"] = "false"


builder = StateGraph(AgentState)

builder.add_node("scout_worker", scout_node)
builder.add_edge(START, "scout_worker")
builder.add_edge("scout_worker", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
