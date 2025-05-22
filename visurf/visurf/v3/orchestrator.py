# main.py
import asyncio
from core.state import AgentState
from core.graph_builder import create_graph
import os
from dotenv import load_dotenv

async def run_agent_system(user_prompt: str):
    """
    Initializes and runs the web interaction agent system with a given user prompt.
    """
    load_dotenv() # Load environment variables (like GOOGLE_API_KEY)

    print(f"--- Starting Web Agent System for Prompt: '{user_prompt}' ---")

    # Create the graph
    graph = create_graph()

    # Define the initial state for the graph.
    # The 'user_prompt' is essential to kick off the process.
    # 'next_action_suggestion' is set to 'INITIALIZE' to signal the Goal Analyzer
    # to begin breaking down the user's request.
    initial_state: AgentState = {
        "user_prompt": user_prompt,
        "current_goal": "Initial goal analysis.",
        "sub_goals_achieved": [],
        "next_action_suggestion": "INITIALIZE",
        "action_Fdata": {},
        "current_url": None,
        "html_content": None,
        "page_elements": [],
        "action_history": [],
        "extracted_data": {},
        "is_goal_achieved": False,
        "status_message": "System starting.",
        "error_message": None,
        "last_action_feedback": None
    }

    # Stream the graph execution
    try:
        # The .astream() method allows you to get output at each step of the graph.
        async for state in graph.astream(initial_state):
            # The 'state' variable here contains the *entire* AgentState after each node execution.
            # You can print relevant parts of the state to observe progress.
            current_node = list(state.keys())[-1] # Get the name of the last executed node
            print(f"\n--- Current Node: {current_node} ---")
            print(f"Status: {state[current_node].get('status_message', 'No status message')}")
            print(f"Next Action Suggestion: {state[current_node].get('next_action_suggestion')}")
            print(f"Is Goal Achieved: {state[current_node].get('is_goal_achieved')}")
            # You might want to print more details based on your debugging needs
            # print(f"Full State After Node: {state[current_node]}")

        # After the graph finishes (either by "DONE" or "ERROR")
        final_state = await graph.ainvoke(initial_state) # Re-invoke to get the final state cleanly
        print("\n--- Graph Execution Finished ---")
        print(f"Final Status: {final_state['status_message']}")
        print(f"Goal Achieved: {final_state['is_goal_achieved']}")
        if final_state.get('extracted_data'):
            print(f"Extracted Data: {final_state['extracted_data']}")
        if final_state.get('error_message'):
            print(f"Error: {final_state['error_message']}")

    except Exception as e:
        print(f"\n!!! An unexpected error occurred during graph execution: {e} !!!")
    finally:
        # Ensure browser is closed regardless of success or failure
        print("\n--- Cleaning up browser resources ---")
        await graph.goal_analyzer_agent.scraper.close()
        # website_analyzer_agent also holds a reference to the scraper
        # We only need to call close on one instance of the scraper.
        # Alternatively, you could have a dedicated cleanup function in graph_builder.py
        # or manage the scraper as a singleton.

# Example usage:
if __name__ == "__main__":
    # You need to run this within an asyncio event loop.
    # The default behavior of `asyncio.run()` is suitable here.
    asyncio.run(run_agent_system("Navigate to example.com and extract the main heading."))
    # asyncio.run(run_agent_system("Go to google.com and search for 'current weather in London'."))