import asyncio

from graph import graph


async def debug_graph() -> None:
    # Initial state
    initial_input = {
        "query": "Últimos árticulos e intervenciones de Juan Manuel de Prada May 2026",
        "findings": [],
        "iteration": 0,
        "critic_feedback": None,
        "final_report": None,
    }

    # Configuration with a unique thread_id
    config = {"configurable": {"thread_id": "handshake_test_001"}}

    # Run the graph
    print("--- Starting Graph Execution ---")
    async for event in graph.astream(initial_input, config=config):
        for node_name, state_update in event.items():
            print(f"\n📍 Node '{node_name}' finished.")
            print(f"📊 State Update: {state_update}")

    # --- THE MEMORY CHECK ---
    # This is how you verify the state was persisted
    final_state = graph.get_state(config)
    print("\n--- Final Memory State ---")
    print(f"Findings Count: {len(final_state.values['findings'])}")
    for i, finding in enumerate(final_state.values["findings"]):
        print(f"[{i}] {finding.title}: {finding}...")


if __name__ == "__main__":
    asyncio.run(debug_graph())
